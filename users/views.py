from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from users.models import User
from users.serializers import UserCRUDSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserCRUDSerializer
    permission_classes = [IsAdminUser]
