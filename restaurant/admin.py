from django.contrib import admin
from .models import Item, OrderItem, Order, Payment, BillingAddress, Coupon
# Register your models here.

def make_refund_accepted(admin, modeladmin, queryset):
    queryset.update(refund_requested=False, refund_granted=True)
make_refund_accepted.short_description = 'update orders to refund granted'

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ref_code',
                    'ordered',
                    'being_delivered',
                    'received',
                    'refund_requested',
                    'refund_granted',
                    # 'shipping_address',
                    'billing_address',
                    'payment',
                    'coupon'
                    ]
    list_display_links = [
        'user',
        # 'shipping_address',
        'billing_address',
        'payment',
        'coupon'
    ]
    list_filter = ['ordered',
                   'being_delivered',
                   'received',
                   'refund_requested',
                   'refund_granted'
                   ]
    search_fields = [
    'user__username',
    'ref_code'
    ]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'zipcode',
        #         # 'address_type',
        #         # 'default'
    ]
#     list_filter = ['default', 'address_type', 'country']
#     search_fields = ['user', 'street_address', 'apartment_address', 'zip']


class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'amount']


class OrderItemsAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'item',
        'cartitem',
        'ordered'
    ]


class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'stripe_charge_id',
        'user',
        'amount',
        'timestamp'
    ]


class ItemAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'price',
        'discount_price',
        'veg_or_nonveg',
        'quantity',
    ]


admin.site.register(Item, ItemAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(OrderItem, OrderItemsAdmin)
admin.site.register(BillingAddress, AddressAdmin)
admin.site.register(Order, OrderAdmin)
