from rest_framework.viewsets import ModelViewSet
from product.models import Category, Product
from product.serializers import CategorySerializer, ProductSerializer
from users.permissions import IsAdminOrManagerOrReadOnly


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrManagerOrReadOnly]


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related("category").order_by("name")
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrManagerOrReadOnly]

