from django.db import models
from django.conf import settings
from PIL import Image
from django.shortcuts import reverse

dish_type = (('Nonveg', 'N'), ('Veg', 'V'))
quantity = (('250gm', '250gm'), ('500gm', '500gm'), ('1kg', '1kg'), ('1', '1'))
# Create your models here.
class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    veg_or_nonveg = models.CharField(choices=dish_type, max_length=20)
    quantity = models.CharField(choices=quantity, max_length=20)
    image = models.ImageField(upload_to='dish_images', default='default.jpg')
    slug = models.SlugField()

    def save(self):
        super().save()
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300,300)
            img.thumbnail(output_size)
            img.save(self.image.path)

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
        return f"new order is {self.item.title} from {self.user.username} cart {self.cartitem}"

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    order_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total
        
    def __str__(self):
        return self.user.username
    