from rest_framework import generics, viewsets, permissions, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum
from django.contrib.auth.models import User
from .models import InventoryItem, InventoryChange
from .serializers import UserSerializer, InventoryItemSerializer, InventoryChangeSerializer
from rest_framework.pagination import PageNumberPagination
from .pagination import InventoryItemPagination 

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

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

                # Filter by price range
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price is not None:
            queryset = queryset.filter(price__gte=float(min_price))
        if max_price is not None:
            queryset = queryset.filter(price__lte=float(max_price))
        if max_price is not None:
            queryset = queryset.filter(price__lte=float(max_price))
                    
                    # Filter by low stock
        low_stock = self.request.query_params.get('low_stock', None)
        if low_stock is not None:
            queryset = queryset.filter(quantity__lte=int(low_stock))   
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        
        # Get the old quantity before saving
        old_quantity = serializer.instance.quantity
        
        # Save the updated instance
        instance = serializer.save(user=self.request.user)
        
        # Create inventory change record if quantity changed
        if old_quantity != instance.quantity:
            InventoryChange.objects.create(
                item=instance,
                previous_quantity=old_quantity,
                new_quantity=instance.quantity,
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
    pagination_class = InventoryItemPagination

    def get_queryset(self):
        return InventoryChange.objects.filter(
            item__user=self.request.user
        ).order_by('-date_changed')


class InventoryItemPagination(PageNumberPagination):
    page_size = 10
