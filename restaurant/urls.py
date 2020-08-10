from django.urls import path
from . import views

app_name = 'restaurant'
urlpatterns = [
    path('', views.HomeView.as_view(), name="homePage"),
    path('checkout/', views.checkout, name="checkOut"),
    path('dish/<slug>/', views.DishDetailView.as_view(), name="dish"),
    path('add-to-cart/<slug>/', views.add_to_cart, name="add-to-cart"),
    path('remove-from-cart/<slug>/', views.remove_from_cart, name="remove-from-cart"),
    path('order-summary/', views.OrderSummaryView.as_view(), name="order-summary")
]