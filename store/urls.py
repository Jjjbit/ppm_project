from django.urls import path
from .views import (ProductDetailView, category_products, ProductListView)


urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('category/<int:category_id>/', category_products, name='category_products'),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product_detail")
]

