from django.contrib import admin
from .models import InventoryItem, InventoryChange

admin.site.register(InventoryItem)
admin.site.register(InventoryChange)