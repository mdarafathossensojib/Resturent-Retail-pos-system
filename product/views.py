from rest_framework.viewsets import ModelViewSet
from product.models import Category, Product
from product.serializers import CategorySerializer, ProductSerializer
from product.permissions import IsAdminOrManagerOrReadOnly
from product.paginations import ProductPagination
from django.db.models import Count


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.annotate(product_count=Count("products")).order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrManagerOrReadOnly]
    pagination_class = ProductPagination


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related("category").order_by("name")
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrManagerOrReadOnly]
    pagination_class = ProductPagination

