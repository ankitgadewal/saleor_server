from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.views.generic import ListView, DetailView, View, TemplateView
from .models import Item, Order, OrderItem, BillingAddress, Payment, Coupon, Refund
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from . forms import CheckoutForm, UserUpdateForm, CouponForm, RefundForm
from django.views.decorators.csrf import csrf_exempt
from .paytm import Checksum
from django.core.mail import send_mail
import stripe
import random
import string
stripe.api_key = settings.STRIPE_SECRET_KEY
MERCHANT_KEY = 'yLtLHOrBIro7O@j4'


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


class PaytmPaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        print(self.request.user.username)
        order = Order.objects.get(user=self.request.user, ordered=False)
        params_dict = {
            'MID': 'wgyjVw30068262008394',
            'ORDER_ID': create_ref_code(),
            'TXN_AMOUNT': str(order.get_total()),
            'CUST_ID': self.request.user.email,
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE': 'WEBSTAGING',
            'CHANNEL_ID': 'WEB',
            'CALLBACK_URL': 'https://ankitgadewal16.pythonanywhere.com/purchase/handle_request/',
        }
        params_dict['CHECKSUMHASH'] = Checksum.generate_checksum(
            params_dict, MERCHANT_KEY)
        params_dict['user'] = str(self.request.user.username)
        return render(self.request, 'restaurant/paytmpayment.html', {'params_dict': params_dict})


@csrf_exempt
def handle_paytm_request(request):
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            return render(request, 'restaurant/paymentstatus.html', {'response': response_dict})
            # newpremium = Premium(order_id=order_id, charge=int(charge))
            # newpremium.save()
        else:
            print('order was not successful because of ' +
                  response_dict['RESPMSG'])
            return render(request, 'restaurant/paymentstatus.html', {'response': response_dict})


class HomeView(ListView):
    model = Item
    template_name = 'restaurant/home-page.html'


class SearchView(ListView):
    model = Item
    template_name = 'restaurant/search.html'

    def get_queryset(self):
        query = self.request.GET['query']
        if len(query) > 50 or len(query) < 1:
            dishes = []
        else:
            dishes = Item.objects.filter(title__icontains=query)
        return dishes


class ProfileView(LoginRequiredMixin, View):
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


class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            form = CheckoutForm()
            coupons = Coupon.objects.all()
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'form': form,
                'order': order,
                'couponform': CouponForm(),
                'coupons': coupons
            }
            oldaddress = BillingAddress.objects.filter(user=self.request.user)
            if oldaddress.exists():
                context.update({'oldaddress': oldaddress[0]})
            if order.get_total() > 0:
                return render(self.request, 'restaurant/checkout-page.html', context)
            else:
                messages.warning(
                    self.request, 'please add some items to your cart before checkout')
                return redirect('/')
        except ObjectDoesNotExist:
            messages.warning(
                self.request, 'please add some items to your cart before checkout')
            return redirect('restaurant:homePage')

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            print(order)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                contact_no = form.cleaned_data.get('contact_no')
                zipcode = form.cleaned_data.get('zipcode')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    contact_no=contact_no,
                    zipcode=zipcode
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                return redirect('restaurant:payment-method')
            messages.info(self.request, 'checkout failed')
            return redirect('restaurant:checkOut')

        except ObjectDoesNotExist:
            messages.warning(self.request, "Your cart is empty")
            return redirect('restaurant:order-summary')


def save_addr(request):
    found_address = BillingAddress.objects.filter(
        user=request.user, street_address=request.POST['street_address'])[0]
    order = Order.objects.get(user=request.user, ordered=False)
    order.billing_address = found_address
    order.save()
    return redirect('restaurant:payment-method')


class PaymentMehodView(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'restaurant/payment_choices.html')


class PaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if order.billing_address:
                return render(self.request, 'restaurant/payment.html', {'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY, 'order': order})
            else:
                messages.warning(self.request, 'please add a billing address')
                return redirect('restaurant:checkOut')
        except ObjectDoesNotExist:
            messages.warning(
                self.request, 'You don\'t have any item in your cart')
            return redirect('/')

    def post(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            token = self.request.POST.get('stripeToken')
            amount = int(order.get_total())
            charge = stripe.Charge.create(
                amount=amount,
                currency="inr",
                source=token,
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
            order.ref_code = create_ref_code()
            order.save()
            send_mail(
                'Congratulations!! Order placed',
                f'hello sir we are very happy to say that your order is suucessfully placed and we received Rs {payment.amount} Your order will be deliverd asap Happy Shopping.',
                'ankitgadewal11@gmail.com',
                ['alkeshk99@gmail.com'],
                fail_silently=False,
            )
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
            # Something else happened, completely unrelated to Stripe
            messages.error(
                self.request, "something serious error, we will be notified...")
            return redirect('/')


class DishDetailView(DetailView):
    model = Item
    template_name = 'restaurant/dish-page.html'
    context_object_name = 'item'


class MyOrdersView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        orderitem = Order.objects.filter(
            user=self.request.user, ordered=True)[::-1]
        context = {
            'orderitem': orderitem
        }
        return render(self.request, 'restaurant/my_orders.html', context)


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            return render(self.request, 'restaurant/order-summary.html', {'object': order})
        except ObjectDoesNotExist:
            messages.warning(self.request, "Your cart is empty")
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
            messages.info(
                request, f"{order_item.item.title} Quantity Updated to {order_item.cartitem}")
            return redirect("restaurant:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "Item added to your cart")
            return redirect("restaurant:homePage")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user,
            order_date=ordered_date,
        )
        order.items.add(order_item)
        messages.info(request, "Item added to your cart")
        return redirect("restaurant:order-summary")
    return redirect("restaurant:homePage")


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
            order_item.delete()
            messages.info(
                request, f"You've removed {order_item.item.title} from your cart")
            return redirect("restaurant:order-summary")
        else:
            messages.info(request, "not an active order to your cart")
            return redirect("restaurant:homePage")
    else:
        messages.info(request, "no orders found")
        return redirect("restaurant:homePage")
    return redirect("restaurant:homePage")


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
                messages.info(
                    request, f"You've changed {order_item.item.title} QUANTITY to {order_item.cartitem}")
                return redirect("restaurant:order-summary")
            else:
                order.items.remove(order_item)
                order_item.delete()
                messages.info(
                    request, f"You've removed {order_item.item.title} from your cart")
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
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                applied_code = Coupon.objects.get(code=code)
                if order.get_total() >= applied_code.min_order_value:
                    order.coupon = Coupon.objects.get(code=code)
                    order.save()
                    messages.success(
                        self.request, f"Voila!! Successfully applied Coupon Code {order.coupon}")
                    return redirect("restaurant:checkOut")
                else:
                    messages.warning(
                        self.request, f"can\'t applied Coupon Code. amount should be greater than {applied_code.min_order_value}/-")
                    return redirect("restaurant:checkOut")
            except ObjectDoesNotExist:
                messages.warning(
                    self.request, f"The Coupon {order.coupon} is invalid or Expired")
                return redirect("restaurant:checkOut")


class RemoveCouponView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        order.coupon = None
        order.save()
        messages.success(self.request, f"promocode removed")
        return redirect("restaurant:checkOut")


class RequestRefundView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "restaurant/request-refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("restaurant:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("restaurant:request-refund")
