from rest_framework.pagination import PageNumberPagination

class InventoryItemPagination(PageNumberPagination):
    page_size = 10