from django.urls import path
from .views import (StoreView, StoreCategoryProductsView, add_product)


urlpatterns = [
    path('<int:seller_id>/', StoreView.as_view(), name='store_dashboard'),
    path('<int:seller_id>/category/<int:category_id>/', StoreCategoryProductsView.as_view(), name='store_category_products'),
    path('<int:seller_id>/add-product/', add_product, name='add_product'),
]

