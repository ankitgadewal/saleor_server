from django import template
from restaurant.models import Order

register = template.Library()

@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        queryset = Order.objects.filter(user=user, ordered=False)
        if queryset.exists():
            return queryset[0].items.count()
    return 0