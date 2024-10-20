from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, InventoryItemViewSet, InventoryChangeViewSet
from .auth import CustomAuthToken

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'items', InventoryItemViewSet, basename='inventoryitem')
router.register(r'changes', InventoryChangeViewSet, basename='inventorychange')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', CustomAuthToken.as_view(), name='api_token_auth'),

]