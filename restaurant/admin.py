from django.contrib import admin
from .models import Item, OrderItem, Order, Payment, BillingAddress, Coupon, ContactUs

def make_refund_accepted(admin, modeladmin, queryset):
    queryset.update(refund_requested=False, refund_granted=True)
make_refund_accepted.short_description = 'refund granted'

def make_refund_completed(admin, modeladmin, queryset):
    queryset.update(refund_completed=True)
make_refund_completed.short_description = 'refund completed'

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ref_code',
                    'order_date',
                    'ordered',
                    'payment',
                    'billing_address',
                    'status',
                    'refund_requested',
                    'refund_granted',
                    'refund_completed',
                    'coupon'
                    ]
    list_display_links = [
        'user',
        'billing_address',
        'payment',
        'coupon'
    ]
    list_filter = ['ordered',
                   'refund_requested',
                   'refund_granted'
                   ]
    search_fields = [
    'user__username',
    'ref_code'
    ]
    actions = [make_refund_accepted, make_refund_completed]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'contact_no',
        'country',
        'zipcode',
    ]
    list_filter = ['country']
    search_fields = ['user__username', 'street_address', 'apartment_address', 'zipcode']


class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'amount']

class OrderItemsAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'item',
        'cartitem',
        'ordered',
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

class ContactAdmin(admin.ModelAdmin):
    list_display = [
        'customer_name',
        'query',
        'mobile_no',
        'timestamp'
    ]


admin.site.register(Item, ItemAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(OrderItem, OrderItemsAdmin)
admin.site.register(BillingAddress, AddressAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(ContactUs, ContactAdmin)
