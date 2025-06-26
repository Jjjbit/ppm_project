from django.urls import path
from .views import (StoreView, StoreCategoryProductsView, AddProductView,
                    EditProductView, DeleteProductView, AddStoreCategoryView, EditStoreCategoryView, DeleteStoreCategoryView)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('<int:seller_id>/', StoreView.as_view(), name='store_dashboard'),
    path('<int:seller_id>/category/<int:category_id>/', StoreCategoryProductsView.as_view(), name='store_category_products'),
    path('<int_seller_id>/add-store-category/', AddStoreCategoryView.as_view(), name='add_store_category'),
    path('<int:seller_id>/edit-store-category/<int:pk>/', EditStoreCategoryView.as_view(), name='edit_store_category'),
    path('<int:seller_id>/delete-store-category/<int:pk>/', DeleteStoreCategoryView.as_view(), name='delete_store_category'),
    path('<int:seller_id>/add-product/', AddProductView.as_view(), name='add_product'),
    path('product/<int:pk>/edit/', EditProductView.as_view(), name='edit_product'),
    path('product/<int:pk>/delete/', DeleteProductView.as_view(), name='delete_product'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

