from django.db import models
from django.conf import settings
from PIL import Image
from django.shortcuts import reverse
from django_countries.fields import CountryField

dish_type = (('Nonveg', 'N'), ('Veg', 'V'))
quantity = (('250gm', '250gm'), ('500gm', '500gm'), ('1kg', '1kg'), ('1', '1'))
# Create your models here.
class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    veg_or_nonveg = models.CharField(choices=dish_type, max_length=20)
    quantity = models.CharField(choices=quantity, max_length=20)
    image_url = models.URLField()
    slug = models.SlugField()

    # def save(self):
    #     super().save()
    #     img = Image.open(self.image.path)
    #     if img.height > 300 or img.width > 300:
    #         output_size = (300,300)
    #         img.thumbnail(output_size)
    #         img.save(self.image.path)

    def get_absolute_url(self):
        return reverse("restaurant:dish", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("restaurant:add-to-cart", kwargs={
            'slug': self.slug
        })
    
    def get_remove_from_cart_url(self):
        return reverse("restaurant:remove-from-cart", kwargs={
            'slug': self.slug
        })

    def __str__(self):
        return self.title

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    cartitem = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def get_total_item_price(self):
        return self.cartitem * self.item.price

    def get_total_item_discount_price(self):
        return self.cartitem * self.item.discount_price

    def save_on_bill(self):
        return self.get_total_item_price() - self.get_total_item_discount_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_item_discount_price()
        return self.get_total_item_price()

    def __str__(self):
        return f"{self.item.title}"

order_status = (('not_accepted', 'not_accepted'),('order_accepted','order_accepted'), ('order_cancelled', 'order_cancelled'), ('on_the_way', 'on_the_way'), ('delivered', 'delivered'))

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    order_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey('BillingAddress', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    status = models.CharField(max_length=50, choices=order_status, default='not_accepted')
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    refund_completed = models.BooleanField(default=False)

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total
        
    # def __str__(self):
    #     return self.user.username

class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zipcode = models.CharField(max_length=10)

    def __str__(self):
        return self.street_address
    
    class Meta:
        verbose_name_plural = 'Addresses'

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.stripe_charge_id

class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()
    min_order_value = models.FloatField(default=10, null=True, blank=True)
    expire_in = models.DateTimeField()

    def __str__(self):
        return self.code

class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"