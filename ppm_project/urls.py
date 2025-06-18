"""
URL configuration for ppm_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from store.views import ProductDetailView, CategoryProductsView, ProductListView, CreateStoreView, EditProductView, \
    DeleteProductView
from store.views import add_to_cart

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ProductListView.as_view(), name='home'),  # new
    path('category/<int:category_id>/', CategoryProductsView.as_view(), name='category_products'),  # new
    path('users/', include('users.urls')), # new
    path('users/', include('django.contrib.auth.urls')), #new
    path('create-store/', CreateStoreView.as_view(), name='create_store'),
    path('store/', include('store.urls')),  # new
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
    path('product/<int:pk>/edit/', EditProductView.as_view(), name='edit_product'),
    path('product/<int:pk>/delete/', DeleteProductView.as_view(), name='delete_product'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)