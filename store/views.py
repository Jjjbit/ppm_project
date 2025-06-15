from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from .models import Product, Category, Cart, CartItem, Order, OrderItem
#from django.utils import timezone
from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProductForm, CategoryForm
from .permissions import IsStoreManager
from django.core.exceptions import PermissionDenied
#from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
#from django.http import HttpResponseRedirect


def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'category_products.html', {
        'category': category,
        'products': products
    })



class ProductListView(ListView):
    model = Product
    template_name = 'product_list.html'
    #context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        category_id = self.request.GET.get('category')
        if category_id:
            return Product.objects.filter(category_id=category_id)
        return Product.objects.all()

class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    #context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_products'] = Product.objects.filter(category=self.object.category).exclude(id=self.object.id)[:4]
        return context

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
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        return redirect('product_list')
    return render(request, 'edit_product.html', {'form': form})

@login_required
@store_manager_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('product_list')




# def product_list(request):
#     products = Product.objects.all()
#     paginator = Paginator(products, 9)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     return render(request, 'product_list.html', {'page_obj': page_obj})

