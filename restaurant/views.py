from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from .models import Item, Order, OrderItem
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist


class HomeView(ListView):
    model = Item
    template_name = 'restaurant/home-page.html'

@login_required
def checkout(request):
    return render(request, 'restaurant/checkout-page.html')

class DishDetailView(DetailView):
    model = Item
    template_name = 'restaurant/dish-page.html'
    context_object_name = 'item'

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            return render(self.request, 'restaurant/order-summary.html', {'object':order})
        except ObjectDoesNotExist:
            messages.error(self.request, "Your cart is empty")
            return redirect('/')
        return render(self.request, 'restaurant/order-summary.html')

@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():   
            order_item.cartitem += 1
            order_item.save()
            messages.info(request, "Item added to your cart")
        else:
            order.items.add(order_item)
            messages.info(request, "Item added to your cart")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user,
            order_date=ordered_date,
        )
        order.items.add(order_item)
        messages.info(request, "Item added to your cart")
    return redirect("restaurant:dish", slug=slug)

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "Item removed from your cart")
        else:
            messages.info(request, "not an active order to your cart")
            return redirect("restaurant:dish", slug=slug)
    else:
        messages.info(request, "no orders found")
        return redirect("restaurant:dish", slug=slug)
    return redirect("restaurant:dish", slug=slug)
