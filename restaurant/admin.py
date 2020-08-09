from django.contrib import admin
from .models import Item, OrderItem, Order
# Register your models here.

admin.site.register((Item, OrderItem, Order))
