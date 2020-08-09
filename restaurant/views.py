from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Item

class HomeView(ListView):
    model = Item
    template_name = 'restaurant/home-page.html'

def homepage(request):
    context = {
        'items':Item.objects.all()
    }
    return render(request, 'restaurant/home-page.html', context)

def checkout(request):
    return render(request, 'restaurant/checkout-page.html')

def dish(request):
    return render(request, 'restaurant/dish-page.html')
