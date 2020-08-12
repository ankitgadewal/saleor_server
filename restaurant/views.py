from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View, TemplateView
from .models import Item, Order, OrderItem, BillingAddress
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from . forms import CheckoutForm, UserUpdateForm

class HomeView(ListView):
    model = Item
    template_name = 'restaurant/home-page.html'

class ProfileView(View):
    def get(self, *args, **kwargs):
        u_form = UserUpdateForm(instance=self.request.user)
        return render(self.request, 'restaurant/profile.html', {'u_form':u_form})

    def post(self, *args, **kwargs):
        if self.request.method == 'POST':
            u_form = UserUpdateForm(self.request.POST, instance=self.request.user)
            if u_form.is_valid():
                u_form.save()
                messages.success(self.request, 'Your Profile has been Updated Successfully')
                return redirect('restaurant:profile')

class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        return render(self.request, 'restaurant/checkout-page.html', {'form':form})

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zipcode = form.cleaned_data.get('zipcode')
                # same_billing_address = form.cleaned_data.get('same_billing_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user = self.request.user,
                    street_address = street_address,
                    apartment_address = apartment_address,
                    country = country,
                    zipcode = zipcode
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                return redirect('restaurant:checkOut')
            messages.info(self.request, 'checkout failed')
            return redirect('restaurant:checkOut')
                
        except ObjectDoesNotExist:
            messages.error(self.request, "Your cart is empty")
            return redirect('restaurant:order-summary')

class PaymentView(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'restaurant/payment.html')

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
            return redirect("restaurant:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "Item added to your cart")
            return redirect("restaurant:dish", slug=slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user,
            order_date=ordered_date,
        )
        order.items.add(order_item)
        messages.info(request, "Item added to your cart")
        return redirect("restaurant:order-summary")
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
            return redirect("restaurant:order-summary")
        else:
            messages.info(request, "not an active order to your cart")
            return redirect("restaurant:dish", slug=slug)
    else:
        messages.info(request, "no orders found")
        return redirect("restaurant:dish", slug=slug)
    return redirect("restaurant:dish", slug=slug)

@login_required
def remove_single_item_from_cart(request, slug):
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
            if order_item.cartitem > 1:
                order_item.cartitem -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "Item quantity updated")      
            return redirect("restaurant:order-summary")
        else:
            messages.info(request, "not an active order to your cart")
            return redirect("restaurant:order-summary")
    else:
        messages.info(request, "no orders found")
        return redirect("restaurant:dish", slug=slug)
    return redirect("restaurant:dish", slug=slug)



