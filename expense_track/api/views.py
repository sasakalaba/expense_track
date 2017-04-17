from rest_framework import status, viewsets, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import (
    UserSerializer,
)


@api_view()
def not_found_404(request):
    """
    404 view
    """
    return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)


class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)
