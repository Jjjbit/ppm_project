from django.db import models
from django.conf import settings
from django.utils import timezone
from users.models import CustomUser
import os

class Store(models.Model):
    owner = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='store')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class StoreCategory(models.Model):
    name = models.CharField(max_length=100)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='categories')

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    discount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True )
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    store_category = models.ForeignKey(StoreCategory, null=True, blank=True, on_delete=models.SET_NULL)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.price} - {self.seller.username}"

    def get_image_url(self):
        if self.image:
            return self.image.url
        return "https://placehold.co/400x400"

    def delete(self, *args, **kwargs):
        CartItem.objects.filter(product=self).delete()

        if self.image:
            image_path = os.path.join(settings.MEDIA_ROOT, self.image.name)
            if os.path.isfile(image_path):
                os.remove(image_path)
        super().delete(*args, **kwargs)

    def get_discount_price(self):
        if self.discount and self.discount < 0:
            return round(self.price * (1 + self.discount / 100), 2)
        return self.price

    def get_discount_percentage(self):
        if self.discount and self.discount< 0:
            return round(self.discount, 2)
        return 0


class Order(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return sum(item.quantity * item.price_at_purchase for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=8, decimal_places=2, null=False)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sold_items', on_delete=models.SET_NULL, null=True)

class Cart(models.Model):
    # session_key = models.CharField(max_length=40, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.user.is_store_manager:
            raise ValueError("Store managers can't have carts.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Cart"

    def total_price(self):
        return sum(item.subtotal() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.product.get_discount_price() * self.quantity


class ReturnRequest(models.Model):
    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE, related_name='return_request')
    reason = models.TextField()
    approved = models.BooleanField(null=True)  # None: pending, True: approved, False: rejected
    created_at = models.DateTimeField(default=timezone.now)


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)


