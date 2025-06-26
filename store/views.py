from django.urls import reverse_lazy,  reverse
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib import messages
from .models import Product, Category, Cart, CartItem, Order, OrderItem, Store, Wishlist, ReturnRequest, StoreCategory
from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProductForm, ReturnRequestForm, StoreCategoryForm
from django.core.exceptions import PermissionDenied
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from users.models import CustomUser
from django.http import Http404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from PIL import Image
from io import BytesIO
from django.core.files.base import  ContentFile

class CreateStoreView(LoginRequiredMixin, CreateView):
    model = Store
    fields = ['name']
    template_name = 'create_store.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

#mostra tutti i prodotti di una categoria specifica del sito
class CategoryProductsView(ListView):
    model = Product
    template_name = "category_products.html"
    paginate_by = 9

    def get_queryset(self):
        category_id = self.kwargs["category_id"]
        # products = Product.objects.filter(category_id=category_id)
        #category = get_object_or_404(Category, id=category_id)
        return Product.objects.filter(category_id=category_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs["category_id"]
        context["category"] = get_object_or_404(Category, id=category_id)
        context["categories"] = Category.objects.all()
        return context

#mostra tutti i prodotti di una categoria specifica di un negozio
class StoreCategoryProductsView(ListView):
    model = Product
    template_name = "store_category_products.html"
    paginate_by = 9

    def __init__(self):
        super().__init__()
        self.seller = None

    def dispatch(self, request, *args, **kwargs):
        self.seller = CustomUser.objects.get(pk=self.kwargs['seller_id'])
        return super().dispatch(request, *args, **kwargs)


    def get_queryset(self):
        seller_id = self.kwargs['seller_id']
        store_category_id = self.kwargs['category_id']
        return Product.objects.filter(seller__id=seller_id, store_category__id=store_category_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seller_id = self.kwargs['seller_id']
        context['seller'] = get_object_or_404(CustomUser, id=seller_id)
        context['category'] = get_object_or_404(StoreCategory, id=self.kwargs['category_id'])
        context["is_owner"] = self.request.user.is_authenticated and self.request.user == self.seller
        context["has_products"] = self.get_queryset().exists()
        return context

@login_required
def add_store_category(request, seller_id):
    if request.user.id != seller_id:
        messages.error(request, "You do not have permission to add categories to this store.")
        return redirect('home')

    store=get_object_or_404(Store, owner=request.user)

    if request.method == "POST":
        form = StoreCategoryForm(request.POST)
        if form.is_valid():
            category=form.save(commit=False)
            category.store=store
            category.save()
            return redirect('store_dashboard')
    else:
        form = StoreCategoryForm()
    return render(request, 'add_store_category.html', {'form': form})

class AddStoreCategoryView(LoginRequiredMixin, CreateView):
    model = StoreCategory
    form_class = StoreCategoryForm
    template_name = 'add_store_category.html'

    # def dispatch(self, request, *args, **kwargs):
    #     self.store = get_object_or_404(Store, owner=request.user)
    #     return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.store = self.request.user.store
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('store_dashboard', kwargs={'seller_id': self.request.user.id})


class EditStoreCategoryView(LoginRequiredMixin, UpdateView):
    model = StoreCategory
    form_class = StoreCategoryForm
    template_name = 'edit_store_category.html'

    def get_queryset(self):
        return StoreCategory.objects.filter(store__owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy('store_dashboard', kwargs={'seller_id': self.request.user.id})


class DeleteStoreCategoryView(LoginRequiredMixin, DeleteView):
    model = StoreCategory
    template_name = 'delete_store_category.html'

    def get_queryset(self):
        return StoreCategory.objects.filter(store__owner=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "Category deleted successfully.")
        return reverse_lazy('store_dashboard', kwargs={'seller_id': self.request.user.id})


#mostra tutti i prodotti di un negozio
class StoreView(ListView):
    model = Product
    template_name = "store_dashboard.html"
    paginate_by = 9

    def dispatch(self, request, *args, **kwargs):
        self.seller = CustomUser.objects.get(pk=self.kwargs['seller_id'])
        if not self.seller.is_store_manager or not hasattr(self.seller, 'store'):
            raise Http404("This user does not have a store.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Product.objects.filter(seller=self.seller)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context["seller"] = self.seller #seller è l'utente proprietario del negozio
        context["categories"] =StoreCategory.objects.filter(store=self.seller.store) #categorie dei prodotti del negozio
        context["is_owner"] = user.is_authenticated and user == self.seller #is_owner booleano che indica se l'utente corrente è il proprietario del negozio
        context["is_store_manager"] = user.is_authenticated and user.is_store_manager #is_store_manage booleano che indica se l'utente corrente è un gestore del negozio
        return context

#mostra tutti i prodotti del sito, con paginazione e filtro per categoria
class ProductListView(ListView):
    model = Product
    template_name = 'product_list.html'
    paginate_by = 9

    def get_queryset(self):
        return Product.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context["categories"] = Category.objects.all()
        context["is_store_manager"] = user.is_authenticated and user.is_store_manager
        return context


class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = None
        items=[]
        referer = self.request.META.get('HTTP_REFERER', '')

        if '/store/' in referer:
            context['back_url'] = reverse('store_dashboard', kwargs={'seller_id': self.request.user.id})
        else:
            context['back_url'] = reverse('home')


        if self.request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=self.request.user)
            cart_items = cart.items.select_related('product')
            for item in cart_items:
                if item.product:
                    items.append(item)
                else:
                    item.delete()
                    messages.warning(self.request, "A product in your cart has been removed by the seller.")
        # else:
        #     session_cart = self.request.session.get('cart', {})
        #     updated_session = {}
        #     for product_id_str, quantity in session_cart.items():
        #         try:
        #             product = Product.objects.get(id=product_id_str)
        #             subtotal = quantity * product.get_discount_price()
        #             items.append({
        #                 'product': product,
        #                 'quantity': quantity,
        #                 'subtotal': subtotal,
        #             })
        #             updated_session[product_id_str] = quantity
        #         except Product.DoesNotExist:
        #             messages.warning(self.request, "A product in your cart has been removed by the seller.")
        #
        #     self.request.session['cart'] = updated_session
        context['cart'] = cart
        context['items'] = items
        context['total_price'] = sum(i['subtotal'] if isinstance(i, dict) else i.subtotal() for i in items)
        return context



@csrf_protect
@require_POST
def add_to_cart(request, product_id):
    product=Product.objects.get(id=product_id)

    if product.stock <= 0:
        messages.error(request, "Product is out of stock.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
                cart_item.save()
                messages.success(request, "Successfully added to cart.")
            else:
                messages.warning(request, "Cannot add more than available stock.")
                # return redirect(request.META.get('HTTP_REFERER', '/'))
                return redirect('home')
        else:
            cart_item.quantity =1
            cart_item.save()
            messages.success(request, "Successfully added to cart.")
    # else:
    #     messages.error(request, "You do not have permission to add this product.")
        # session_cart = request.session.get('cart', {})
        # product_id_str = str(product_id)
        # current_qty = session_cart.get(product_id_str, 0)
        #
        # if current_qty < product.stock:
        #     session_cart[product_id_str] = current_qty + 1
        #     request.session['cart'] = session_cart
        #     messages.success(request, "Added to cart.")
        # else:
        #     messages.warning(request, "Cannot add more than available stock.")
    # return redirect(request.META.get('HTTP_REFERER', '/'))
    return redirect('home')


class AddToCartView(LoginRequiredMixin, UpdateView):
    @method_decorator(csrf_protect)
    @method_decorator(require_POST)
    def post(self, request, product_id):
        product = Product.objects.get(id=product_id)
        # try:
        #     product = Product.objects.get(id=product_id)
        # except Product.DoesNotExist:
        #     messages.error(request, "Product not found.")
        #     return redirect(request.META.get('HTTP_REFERER', '/'))

        if product.stock <= 0:
            messages.error(request, "Product is out of stock.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if not created: #prodotto aggiunto esiste già nel carrello
                if cart_item.quantity < product.stock:
                    cart_item.quantity += 1
                    cart_item.save()
                    messages.success(request, "Successfully added to cart.")
                else:
                    messages.warning(request, "Cannot add more than available stock.")
                    return redirect(request.META.get('HTTP_REFERER', '/'))
            else:
                cart_item.quantity = 1
                cart_item.save()
                messages.success(request, "Successfully added to cart.")
        else:
            #messages.warning(request, "You do not have permission to add this product.")
            session_cart = request.session.get('cart', {})
            product_id_str = str(product_id)
            current_qty = session_cart.get(product_id_str, 0)

            if current_qty < product.stock:
                session_cart[product_id_str] = current_qty + 1
                request.session['cart'] = session_cart
                messages.success(request, "Successfully added to cart.")
            else:
                messages.warning(request, "Cannot add more than available stock.")

        return redirect(request.META.get('HTTP_REFERER', '/'))

@require_POST
@login_required
def increase_quantity(request, item_id):
    item=get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if item.quantity < item.product.stock:
        item.quantity += 1
        item.save()
        messages.success(request, "Successfully added to cart.")
    return redirect('cart_view')

class IncreaseQuantityView(View):
      def post(self, request, item_id):
          item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
          if item.quantity <item.product.stock:
              item.quantity+=1
              item.save()
          return redirect('cart_view')

@require_POST
@login_required
def decrease_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()
    return redirect('cart_view')

class DecreaseQuantityView(View):
    def post(self, request, item_id):
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        if item.quantity >1:
            item.quantity-=1
            item.save()
        return redirect('cart_view')

@require_POST
@login_required
def delete_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('cart_view')

class DeleteCartItemView(View):
    def post(self, request, item_id):
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        item.delete()
        return redirect('cart_view')

@require_POST
@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    if not cart.items.exists():
        return redirect('cart_view')

    order = Order.objects.create(buyer=request.user)
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price_at_purchase=item.product.get_discount_price(),
            seller=item.product.seller
        )
        item.product.stock -= item.quantity
        item.product.save()

    cart.items.all().delete()
    return redirect('home')

# class CheckoutView(LoginRequiredMixin, View):
#     def post(self, request):
#         cart=get_object_or_404(Cart, user=self.request.user)
#         if not cart.items.exists():
#             return redirect('cart_view')
#
#         order=Order.objects.create(buyer=self.request.user)
#         for item in cart.items.all():
#             OrderItem.objects.create(
#                 order=order,
#                 product=item.product,
#                 quantity=item.quantity,
#                 price_at_purchase=item.product.get_discount_price(),
#                 seller=item.product.seller
#             )
#             item.product.stock-=item.quantity
#             item.product.save()
#
#         cart.items.all().delete()
#         return redirect('home')


class BuyerOrderListView(LoginRequiredMixin, ListView):
    template_name = 'buyer_order_list.html'

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        referer = self.request.META.get('HTTP_REFERER', '')

        if '/store/' in referer:
            context['back_url'] = reverse('store_dashboard', kwargs={'seller_id': self.request.user.id})
        elif 'users/profile/' in referer:
            context['back_url'] = reverse('profile')
        else:
            context['back_url'] = reverse('home')
        return context


class SellerOrderListView(LoginRequiredMixin, ListView):
    template_name = 'seller_order_list.html'
    context_object_name = 'order_items'
    paginate_by = 20

    def get_queryset(self):
        return OrderItem.objects.filter(seller=self.request.user).select_related('order', 'product', 'order__buyer', 'return_request').order_by('-order__created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_items=context['order_items']
        referer = self.request.META.get('HTTP_REFERER', '')

        for item in order_items:
            item.subtotal=item.quantity*item.price_at_purchase

        if '/store/' in referer:
            context['back_url'] = reverse('store_dashboard', kwargs={'seller_id': self.request.user.id})
        elif 'users/profile/' in referer:
            context['back_url'] = reverse('profile')
        else:
            context['back_url'] = reverse('home')
        return context

class OrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'order_detail.html'
    model = Order
    context_object_name = 'order'

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Order.objects.filter(buyer=user)
        return Order.objects.none()


class WishlistView(LoginRequiredMixin, TemplateView):
    template_name = 'wishlist.html'
    pagination = 9

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        wishlist, _ = Wishlist.objects.get_or_create(user=self.request.user)
        context['products'] = wishlist.products.all()
        referer = self.request.META.get('HTTP_REFERER', '')

        if '/users/profile/' in referer:
            context['back_url'] = reverse('profile')
        else:
            context['back_url'] = reverse('home')
        return context

# class AddToWishlistView(LoginRequiredMixin, View):
#     def post(self, request, product_id):
#         product = get_object_or_404(Product, id=product_id)
#
#         if request.user.is_store_manager:
#             messages.error(request, "Sellers cannot use the wishlist.")
#             return redirect('home')
#
#         wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
#         wishlist.products.add(product)
#         messages.success(request, "Product added to your wishlist.")
#         return redirect(request.META.get('HTTP_REFERER', '/'))
#
# class DeleteFromWishlistView(LoginRequiredMixin, View):
#     def post(self, request, product_id):
#         wishlist = get_object_or_404(Wishlist, user=request.user)
#         product = get_object_or_404(Product, id=product_id)
#         wishlist.products.remove(product)
#         messages.success(request, "Product removed from your wishlist.")
#         return redirect('wishlist_view')

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_store_manager:
        messages.error(request, "Only buyers can use the wishlist.")
        return redirect('home')

    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist.products.add(product)
    messages.success(request, "Product added to your wishlist.")
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def remove_from_wishlist(request, product_id):
    wishlist = get_object_or_404(Wishlist, user=request.user)
    product = get_object_or_404(Product, id=product_id)
    wishlist.products.remove(product)
    messages.success(request, "Product removed from your wishlist.")
    return redirect('wishlist_view')




#mostra i dettagli di un prodotto specifico
class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product=self.get_object()
        context['store']=Store.objects.filter(owner=self.object.seller).first()
        context['is_seller']=product.seller==self.request.user
        referer = self.request.META.get('HTTP_REFERER', '')
        if '/store/' in referer:
            context['back_url'] = reverse('store_dashboard', kwargs={'seller_id': product.seller.id})
        else:
            context['back_url'] = reverse('home')
        return context

# def store_manager_required(view_func):
#     def wrapper(request, *args, **kwargs):
#         if not request.user.is_authenticated or not request.user.is_store_manager:
#             raise PermissionDenied
#         return view_func(request, *args, **kwargs)
#     return wrapper


# @login_required
# @store_manager_required
# def add_product(request, seller_id):
#     if request.user.id != seller_id:
#         raise PermissionDenied("You cannot add products to someone else's store.")
#
#     if request.method == "POST":
#         form = ProductForm(request.POST, request.FILES, user=request.user)
#         if form.is_valid():
#             product=form.save(commit=False)
#             product.seller = request.user
#             product.save()
#             return redirect('store_dashboard', seller_id=request.user.id)
#     else:
#         form = ProductForm(user=request.user)
#     return render(request, 'add_product.html', {'form': form})


def process_image(image_field, filename_base):
    img = Image.open(image_field)
    img = img.convert('RGB')

    width, height = img.size
    min_dim = min(width, height)
    left = (width - min_dim) / 2
    top = (height - min_dim) / 2
    right = (width + min_dim) / 2
    bottom = (height + min_dim) / 2
    img = img.crop((left, top, right, bottom))

    img = img.resize((400, 400), Image.Resampling.LANCZOS)

    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)

    return ContentFile(buffer.read(), name=f'{filename_base}_cropped.jpg')

class AddProductView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'add_product.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.seller = self.request.user
        if form.cleaned_data.get('image'):
            original_image = form.cleaned_data['image']
            form.instance.image = process_image(original_image, original_image.name.split('.')[0])
        return super().form_valid(form)

        # form.instance.seller = self.request.user
        # return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('store_dashboard', kwargs={'seller_id': self.request.user.id})

class EditProductView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    template_name = 'edit_product.html'
    context_object_name = 'product'
    form_class = ProductForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def test_func(self):
        product = self.get_object()
        return self.request.user == product.seller

    # def handle_no_permission(self):
    #     raise PermissionDenied("You do not have permission to edit this product.")

    def get_success_url(self):
        return reverse_lazy('store_dashboard', kwargs={'seller_id': self.request.user.id})

    def form_valid(self, form):
        if 'remove_image' in self.request.POST:
            form.instance.image.delete(save=False)
            form.instance.image = None
        else:
            if form.cleaned_data.get('image'):
                original_image = form.cleaned_data['image']
                form.instance.image = process_image(original_image, original_image.name.split('.')[0])
        return super().form_valid(form)

        # if 'remove_image' in self.request.POST:
        #     form.instance.image.delete(save=False)
        #     form.instance.image = None
        # return super().form_valid(form)



class DeleteProductView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'delete_product.html'

    def test_func(self):
        product = self.get_object()
        return self.request.user == product.seller

    def handle_no_permission(self):
        raise PermissionDenied("You do not have permission to delete this product.")

    def get_success_url(self):
        return reverse_lazy('store_dashboard', kwargs={'seller_id': self.request.user.id})


@login_required
def submit_return_request(request, item_id):
    order_item=get_object_or_404(OrderItem, id=item_id, order__buyer=request.user)

    if hasattr(order_item, 'return_request'):
        messages.warning(request, "You have already submitted a return request for this item.")
        return redirect('buyer_orders')

    if request.method=='POST':
        form=ReturnRequestForm(request.POST)
        if form.is_valid():
            return_request=form.save(commit=False)
            return_request.order_item=order_item
            return_request.save()
            messages.success(request, 'Return request submitted successfully.')
            return redirect('buyer_orders')
    else:
        form=ReturnRequestForm()
    return render(request, 'submit_return_request.html', {'form':form, 'item': order_item})



# class SellerReturnRequestListView(LoginRequiredMixin, View):
#     def get(self, request):
#         return_requests = ReturnRequest.objects.filter(order_item__product__seller=request.user)
#         return render(request, 'seller_return_requests.html', {'return_requests': return_requests})

#seller visualizza tutte le richieste di resi
@login_required
def seller_return_requests(request):
    pending_return_requests=ReturnRequest.objects.filter(order_item__product__seller=request.user, approved__isnull=True)
    return render(request, 'seller_return_requests.html', {'pending_return_requests': pending_return_requests})

@login_required
def approve_return_request(request, request_id):
    return_request=get_object_or_404(ReturnRequest, id=request_id, order_item__product__seller=request.user)

    if request.method=='POST':
        return_request.approved=True
        return_request.save()
        messages.success(request, 'Return approved.')
    return redirect('store_dashboard', seller_id=request.user.id)

@login_required
def reject_return_request(request, request_id):
    return_request = get_object_or_404(ReturnRequest, id=request_id, order_item__product__seller=request.user)

    if request.method == 'POST':
        return_request.approved=False
        return_request.save()
        messages.success(request, 'Return approved.')
    return redirect('store_dashboard', seller_id=request.user.id)

