from rest_framework import viewsets, permissions, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum
from django.contrib.auth.models import User
from .models import InventoryItem, InventoryChange
from .serializers import UserSerializer, InventoryItemSerializer, InventoryChangeSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class InventoryItemViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['category', 'price']
    ordering_fields = ['name', 'quantity', 'price', 'date_added']
    search_fields = ['name', 'description']

    def get_queryset(self):
        queryset = InventoryItem.objects.filter(user=self.request.user)
        min_quantity = self.request.query_params.get('min_quantity', None)
        if min_quantity is not None:
            queryset = queryset.filter(quantity__lte=min_quantity)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        instance = self.get_object()
        old_quantity = instance.quantity
        new_quantity = serializer.validated_data.get('quantity', old_quantity)
        
        serializer.save()
        
        if new_quantity != old_quantity:
            InventoryChange.objects.create(
                item=instance,
                quantity_changed=new_quantity - old_quantity,
                user=self.request.user
            )

    @action(detail=False, methods=['get'])
    def inventory_levels(self, request):
        queryset = self.get_queryset()
        data = queryset.values('category').annotate(total_quantity=Sum('quantity'))
        return Response(data)

class InventoryChangeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InventoryChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return InventoryChange.objects.filter(item__user=self.request.user)