from django.urls import path
from . import views

app_name = 'restaurant'
urlpatterns = [
    path('', views.HomeView.as_view(), name="homePage"),
    path('checkout/', views.CheckoutView.as_view(), name="checkOut"),
    path('dish/<slug>/', views.DishDetailView.as_view(), name="dish"),
    path('add-to-cart/<slug>/', views.add_to_cart, name="add-to-cart"),
    path('remove-from-cart/<slug>/', views.remove_from_cart, name="remove-from-cart"),
    path('order-summary/', views.OrderSummaryView.as_view(), name="order-summary"),
    path('remove-single-item-from-cart/<slug>/', views.remove_single_item_from_cart, name="remove_single_item_from_cart"),
    path('payment/stripe/', views.PaymentView.as_view(), name="payment"),
    path('profile', views.ProfileView.as_view(), name="profile"),
    path('add-coupon/', views.AddCouponView.as_view(), name="add-coupon"),
]