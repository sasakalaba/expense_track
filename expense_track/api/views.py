from django.contrib.auth.models import User
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from expense_trackapp.models import Expense
from .permissions import IsOwnerOrAdmin
from .filters import ExpenseFilter
from .serializers import (
    UserSerializer,
    ExpenseSerializer
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


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [IsOwnerOrAdmin, ]
    lookup_fields = ['username', 'pk']
    filter_class = ExpenseFilter

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Expense.objects.all()
        else:
            return Expense.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user

        if self.request.user.is_superuser:
            username = serializer.initial_data.get('user')
            if username:
                user = User.objects.get(username=username)
        elif self.request.user.is_staff:
            return None

        serializer.save(user=user)
