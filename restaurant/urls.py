from django.urls import path
from . import views

app_name = 'restaurant'
urlpatterns = [
    path('', views.HomeView.as_view(), name="homePage"),
    path('checkout/', views.CheckoutView.as_view(), name="checkOut"),
    path('save_addr', views.save_addr, name="save_addr"),
    path('my-orders', views.MyOrdersView.as_view(), name="myOrders"),
    path('dish/<slug>/', views.DishDetailView.as_view(), name="dish"),
    path('add-to-cart/<slug>/', views.add_to_cart, name="add-to-cart"),
    path('remove-from-cart/<slug>/', views.remove_from_cart, name="remove-from-cart"),
    path('order-summary/', views.OrderSummaryView.as_view(), name="order-summary"),
    path('remove-single-item-from-cart/<slug>/', views.remove_single_item_from_cart, name="remove_single_item_from_cart"),
    path('payment/stripe/', views.PaymentView.as_view(), name="payment"),
    path('profile', views.ProfileView.as_view(), name="profile"),
    path('add-coupon/', views.AddCouponView.as_view(), name="add-coupon"),
    path('remove-coupon/', views.RemoveCouponView.as_view(), name="remove-coupon"),
    path('request-refund', views.RequestRefundView.as_view(), name="request-refund"),
    path('paytm-payment', views.PaytmPaymentView.as_view(), name="paytm-payment"),
    path('purchase/handle_request/', views.handle_paytm_request, name="handle_paytm_request"),
    path('payment-method', views.PaymentMehodView.as_view(), name="payment-method"),
    path('search', views.SearchView.as_view(), name='search'),
]