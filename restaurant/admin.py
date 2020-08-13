from django.contrib import admin
from .models import Item, OrderItem, Order, Payment, BillingAddress, Coupon
# Register your models here.

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered']

admin.site.register((Item, OrderItem, Payment, BillingAddress, Coupon))
admin.site.register(Order, OrderAdmin)
