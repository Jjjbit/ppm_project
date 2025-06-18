from django.urls import reverse_lazy,  reverse
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib import messages
from .models import Product, Category, Cart, CartItem, Order, OrderItem, Store
#from django.utils import timezone
from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import ProductForm
#from .permissions import IsStoreManager
from django.core.exceptions import PermissionDenied
#from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from users.models import CustomUser
from django.http import Http404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
#from django.http import HttpResponseRedirect

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
        category_id = self.kwargs['category_id']
        return Product.objects.filter(seller__id=seller_id, category__id=category_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seller_id = self.kwargs['seller_id']
        context['seller'] = get_object_or_404(CustomUser, id=seller_id)
        context['category'] = get_object_or_404(Category, id=self.kwargs['category_id'])
        context["is_owner"] = self.request.user.is_authenticated and self.request.user == self.seller
        context["has_products"] = self.get_queryset().exists()
        return context


#mostra tutti i prodotti di un negozio
class StoreView(ListView):
    model = Product
    template_name = "store_dashboard.html"
    paginate_by = 9
    # context_object_name = "seller" #urls.py: path('<int:pk>/', StoreView.as_view(), name='store_dashboard')

    # def __init__(self):
    #     super().__init__()
    #     self.seller = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.seller = CustomUser.objects.get(pk=self.kwargs['seller_id'])
            if not self.seller.is_store_manager or not hasattr(self.seller, 'store'):
                raise Http404("This user does not have a store.")
        except CustomUser.DoesNotExist:
            raise Http404("User not found.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Product.objects.filter(seller=self.seller)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context["seller"] = self.seller #seller è l'utente proprietario del negozio
        context["categories"] = Category.objects.filter(product__seller=self.seller).distinct() #categorie dei prodotti del negozio
        context["is_owner"] = user.is_authenticated and user == self.seller #is_owner booleano che indica se l'utente corrente è il proprietario del negozio
        context["is_store_manager"] = user.is_authenticated and user.is_store_manager #is_store_manage booleano che indica se l'utente corrente è un gestore del negozio
        return context



#mostra tutti i prodotti del sito, con paginazione e filtro per categoria
class ProductListView(ListView):
    model = Product
    template_name = 'product_list.html'
    paginate_by = 9

    def get_queryset(self):
        category_id = self.request.GET.get('category')
        if category_id:
            return Product.objects.filter(category_id=category_id)
        return Product.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context["categories"] = Category.objects.all()
        context["is_store_manager"] = user.is_authenticated and user.is_store_manager
        return context




@csrf_protect
@require_POST
def add_to_cart(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        messages.error(request, "Product not found.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if product.stock <= 0:
        messages.error(request, "Product is out of stock.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item = CartItem.objects.filter(cart=cart, product=product).first()
        if cart_item:
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
                cart_item.save()
            else:
                messages.warning(request, "Cannot add more than available stock.")
                return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            CartItem.objects.create(cart=cart, product=product, quantity=1)
            messages.success(request, "Successfully added to cart.")
    else:
        session_cart = request.session.get('cart', {})
        current_qty = session_cart.get(str(product.id), 0)

        if current_qty < product.stock:
            session_cart[str(product.id)] = current_qty + 1
            request.session['cart'] = session_cart
            messages.success(request, "Successfully added to cart.")
        else:
            messages.warning(request, "Cannot add more than available stock.")


    return redirect(request.META.get('HTTP_REFERER', '/'))



class WishlistView(LoginRequiredMixin, TemplateView):
    template_name = 'wishlist.html'


#mostra i dettagli di un prodotto specifico
class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        referer = self.request.META.get('HTTP_REFERER', '')
        if '/store/' in referer:

            seller_id = self.object.seller.id
            context['back_url'] = reverse('store_dashboard', kwargs={'seller_id': seller_id})
        else:
            context['back_url'] = reverse('home')
        return context

def store_manager_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_store_manager:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@store_manager_required
def add_product(request, seller_id):
    if request.user.id != seller_id:
        raise PermissionDenied("You cannot add products to someone else's store.")

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            product=form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect('store_dashboard', seller_id=request.user.id)
    else:
        form = ProductForm(user=request.user)
    return render(request, 'add_product.html', {'form': form})

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
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('store_dashboard', kwargs={'seller_id': self.request.user.id})

class EditProductView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    template_name = 'edit_product.html'
    context_object_name = 'product'
    fields = ['name', 'price', 'discount', 'stock', 'image', 'description']

    def test_func(self):
        product = self.get_object()
        return self.request.user == product.seller

    def handle_no_permission(self):
        raise PermissionDenied("You do not have permission to edit this product.")

    def get_success_url(self):
        return reverse_lazy('store_dashboard', kwargs={'seller_id': self.request.user.id})

    def form_valid(self, form):
        if 'remove_image' in self.request.POST:
            form.instance.image.delete(save=False)
            form.instance.image = None
        return super().form_valid(form)



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
