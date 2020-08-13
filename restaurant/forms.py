from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from django.contrib.auth.models import User
from django import forms

PAYMENT_CHOICES = (
    ('P', 'Paypal'),
    ('S', 'Stripe'))

class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'xyz Nagin Nagar Indore',
        'class':'form-control'
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Apartment or Suite',
        'class':'form-control'
    }))
    country = CountryField(blank_label='(Select Country)').formfield(
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100'
    }))
    zipcode = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    same_billing_address = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    save_info = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices= PAYMENT_CHOICES)


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=None)
    class Meta:
        model = User
        fields = ['username', 'email']

class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Promo Code',
        'class':'form-control',
        'aria-label':"Recipient's username",
        'aria-describedby':"basic-addon2"
    }))