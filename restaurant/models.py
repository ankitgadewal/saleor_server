from django.db import models
from django.conf import settings
from PIL import Image

dish_type = (('Nonveg', 'N'), ('Veg', 'V'))
quantity = (('250gm', '250gm'), ('500gm', '500gm'), ('1kg', '1kg'), ('1', '1'))
# Create your models here.
class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    veg_or_nonveg = models.CharField(choices=dish_type, max_length=20)
    quantity = models.CharField(choices=quantity, max_length=20)
    image = models.ImageField(upload_to='dish_images', default='default.jpg')

    def save(self):
        super().save()
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300,300)
            img.thumbnail(output_size)
            img.save(self.image.path)

    def __str__(self):
        return self.title

class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return self.item

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    order_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    