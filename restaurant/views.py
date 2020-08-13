from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.views.generic import ListView, DetailView, View, TemplateView
from .models import Item, Order, OrderItem, BillingAddress, Payment, Coupon
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from . forms import CheckoutForm, UserUpdateForm, CouponForm
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class HomeView(ListView):
    model = Item
    template_name = 'restaurant/home-page.html'


class ProfileView(View):
    def get(self, *args, **kwargs):
        u_form = UserUpdateForm(instance=self.request.user)
        return render(self.request, 'restaurant/profile.html', {'u_form': u_form})

    def post(self, *args, **kwargs):
        u_form = UserUpdateForm(
            self.request.POST, instance=self.request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(
                self.request, 'Your Profile has been Updated Successfully')
            return redirect('restaurant:profile')


class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        order = Order.objects.get(user=self.request.user, ordered=False)
        return render(self.request, 'restaurant/checkout-page.html', {'form': form, 'order': order,'couponform': CouponForm()})

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
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zipcode=zipcode
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
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            return render(self.request, 'restaurant/payment.html')
        else:
            messages.warning(self.request, 'please add a billing address')
            return redirect('restaurant:checkOut')

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total())

        try:
            stripe.Charge.create(
                amount=amount,
                currency="inr",
                source= token,
                customer  = stripe_customer.id,
            )

            # save payments to our database
            payment = Payment()
            
            payment.stripe_charge_id = charge['id']
            payment.amount = order.get_total()
            payment.user = self.request.user
            payment.save()

            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                 item.save()

            # assigning the payment to the order
            order.ordered = True
            order.payment = payment
            order.save()
            messages.success(self.request, "your payment was sucessful")
            return redirect('/')
 
        except stripe.error.CardError as e:            
            messages.error(self.request, e.error.message)
            return redirect('/')

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, "rate limit error")
            return redirect('/')

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            print(e)
            messages.warning(self.request, "invalid request")
            return redirect('/')

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "authentication error")
            return redirect('/')

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "connection problem")
            return redirect('/')

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request, "something went wrong...")
            return redirect('/')

        except Exception as e:
            print(e)
            # Something else happened, completely unrelated to Stripe
            messages.error(self.request, "something serious error, we will be notified...")
            return redirect('/')


class DishDetailView(DetailView):
    model = Item
    template_name = 'restaurant/dish-page.html'
    context_object_name = 'item'


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            return render(self.request, 'restaurant/order-summary.html', {'object': order})
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

class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=self.request.user, ordered=False)
                order.coupon = Coupon.objects.get(code=code)
                order.save()
                messages.success(self.request, "Voila!! Successfully applied Coupon Code")
                return redirect("restaurant:checkOut")
            except ObjectDoesNotExist:
                messages.warning(self.request, "The Coupon is invalid or Expired")
                return redirect("restaurant:checkOut")