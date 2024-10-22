from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, UserViewSet, InventoryItemViewSet, InventoryChangeViewSet
from .auth import CustomAuthToken

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'items', InventoryItemViewSet, basename='inventoryitem')
router.register(r'changes', InventoryChangeViewSet, basename='inventorychange')
router.register(r'inventory', InventoryItemViewSet, basename='inventory')
router.register(r'inventory-changes', InventoryChangeViewSet, basename='inventory-changes')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('register/', RegisterView.as_view(), name='auth_register'),
]