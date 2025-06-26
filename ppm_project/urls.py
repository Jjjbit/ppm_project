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
from store.views import (
    ProductDetailView,
    CategoryProductsView,
    ProductListView,
    CreateStoreView,
    CartView,
    add_to_cart,
    IncreaseQuantityView,
    increase_quantity,
    DecreaseQuantityView,
    decrease_quantity,
    DeleteCartItemView,
    delete_cart_item,
    checkout,
    BuyerOrderListView,
    SellerOrderListView,
    OrderDetailView,
    add_to_wishlist,
    remove_from_wishlist,
    WishlistView,
    submit_return_request,
    seller_return_requests,
    approve_return_request,
    reject_return_request,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ProductListView.as_view(), name='home'),  # new
    path('category/<int:category_id>/', CategoryProductsView.as_view(), name='category_products'),  # new
    path('users/', include('users.urls')), # new
    path('users/', include('django.contrib.auth.urls')), #new
    path('create-store/', CreateStoreView.as_view(), name='create_store'),
    path('store/', include('store.urls')),  # new
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
    path('cart/', CartView.as_view(), name='cart_view'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    #path('increase-quantity/<int:item_id>/', IncreaseQuantityView.as_view(), name='cart_increase_quantity'),
    path('increase-quantity/<int:item_id>/',increase_quantity, name='cart_increase_quantity'),
    #path('decrease-quantity/<int:item_id>/', DecreaseQuantityView.as_view(), name='cart_decrease_quantity'),
    path('decrease-quantity/<int:item_id>/', decrease_quantity, name='cart_decrease_quantity'),
    #path('delete/<int:item_id>/', DeleteCartItemView.as_view(), name='cart_delete_item'),
    path('delete/<int:item_id>/', delete_cart_item, name='cart_delete_item'),
    #path('checkout/', CheckoutView.as_view(), name='checkout' ),
    path('checkout/', checkout, name='checkout'),
    path('orders/', BuyerOrderListView.as_view(), name='buyer_orders'),
    path('order/retun/<int:item_id>/',submit_return_request,name='submit_return_request'),
    path('orders/sold/', SellerOrderListView.as_view(), name='seller_orders'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/add/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('seller/return-requests/', seller_return_requests, name='seller_return_requests'),
    path('seller/return-requests/<int:request_id>/approve/', approve_return_request, name='approve_return_request'),
    path('seller/return-requests/<int:request_id>/reject/', reject_return_request, name='reject_return_request'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)