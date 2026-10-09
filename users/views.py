from rest_framework.viewsets import ModelViewSet

from users.models import User
from users.serializers import UserCRUDSerializer
from users.permissions import IsAdmin


class UserViewSet(ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserCRUDSerializer
    permission_classes = [IsAdmin]