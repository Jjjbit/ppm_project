from django.urls import path
from .views import (StoreView, StoreCategoryProductsView, AddProductView,
                    EditProductView, DeleteProductView)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('<int:seller_id>/', StoreView.as_view(), name='store_dashboard'),
    path('<int:seller_id>/category/<int:category_id>/', StoreCategoryProductsView.as_view(), name='store_category_products'),
    # path('<int:seller_id>/add-product/', add_product, name='add_product'),
    path('<int:seller_id>/add-product/', AddProductView.as_view(), name='add_product'),
    path('product/<int:pk>/edit/', EditProductView.as_view(), name='edit_product'),
    path('product/<int:pk>/delete/', DeleteProductView.as_view(), name='delete_product'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

