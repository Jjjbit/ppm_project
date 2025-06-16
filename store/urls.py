from django.urls import path
from .views import (StoreView, StoreCategoryProductsView)


urlpatterns = [
    path('', StoreView.as_view(), name='store_dashboard'),
    path('<int:seller_id>/category/<int:category_id>/', StoreCategoryProductsView.as_view(), name='store_category_products'),
]

