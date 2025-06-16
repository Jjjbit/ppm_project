from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from pyexpat.errors import messages

from .models import Product, Category, Cart, CartItem, Order, OrderItem
#from django.utils import timezone
from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProductForm, CategoryForm
#from .permissions import IsStoreManager
from django.core.exceptions import PermissionDenied
#from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from users.models import CustomUser

from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

#from django.http import HttpResponseRedirect


#mostra tutti i prodotti di una categoria specifica del sito
class CategoryProductsView(ListView):
    model = Product
    template_name = "category_products.html"
    paginate_by = 9

    def get_queryset(self):
        category_id = self.kwargs["category_id"]
        category = get_object_or_404(Category, id=category_id)
        return Product.objects.filter(category=category)

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

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["seller"] = self.seller
        context["categories"] = Category.objects.filter(product__seller=self.seller).distinct()
        context["is_owner"] = self.request.user.is_authenticated and self.request.user == self.seller
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
        context["categories"] = Category.objects.all()
        return context


#mostra i dettagli di un prodotto specifico
class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_products'] = Product.objects.filter(category=self.object.category).exclude(id=self.object.id)[:4]
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


def store_manager_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_store_manager:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@store_manager_required
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})


@login_required
@store_manager_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.user != product.seller:
        raise PermissionDenied

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'edit_product.html', {'form': form})

@login_required
@store_manager_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('product_list')


