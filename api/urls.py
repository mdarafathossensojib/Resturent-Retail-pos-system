from django.urls import include, path
from rest_framework.routers import DefaultRouter

from customers.views import CustomerViewSet
from inventory.views import StockMovementViewSet
from payments.views import PaymentViewSet
from product.views import CategoryViewSet, ProductViewSet
from purchases.views import PurchaseItemViewSet, PurchaseViewSet
from sales.views import SaleItemViewSet, SaleViewSet
from suppliers.views import SupplierViewSet
from users.views import UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('customers', CustomerViewSet, basename='customer')
router.register('suppliers', SupplierViewSet, basename='supplier')
router.register('categories', CategoryViewSet, basename='category')
router.register('products', ProductViewSet, basename='product')
router.register('inventory', StockMovementViewSet, basename='stock-movement')
router.register('purchases', PurchaseViewSet, basename='purchase')
router.register('purchase-items', PurchaseItemViewSet, basename='purchase-item')
router.register('sales', SaleViewSet, basename='sale')
router.register('sale-items', SaleItemViewSet, basename='sale-item')
router.register('payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]