from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import MinValueValidator

# Create your models here.
# Section model
class Section(models.Model):
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.category

# CustomUser model
class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# UserAddress model
class UserAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.CharField(max_length=350)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50) # can change later
    state = models.CharField(max_length=50) # can change later

    def __str__(self):
        return self.zip_code

# Product model
class Product(models.Model):
    product_name = models.CharField(max_length=150)
    product_description = models.CharField(max_length=1000)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])
    product_image = models.ImageField(upload_to='', blank=True, null=True)
    stock = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True) # new field
    # change supplier and platform to product class
    supplier = models.CharField(max_length=100) 
    platform = models.CharField(max_length=100)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)

    # method when the stock is or no on 0
    def save(self, *args, **kwargs):
        if self.stock <= 0:
            self.is_active = False
        else:
            self.is_active = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product_name
    
# ShoppingCart model
class ShoppingCart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.id} for {self.user}"

# CartItem model
class CartItem(models.Model):
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])

    # add method to:
    # - identify the unit price of each product 
    # - validate that the quantity is not greater than the available stock
    # - avoid negative or invalid amounts
    def save(self, *args, **kwargs):
        if self.quantity < 1:
            raise ValueError("The quantity cannot be less to 1.")
        
        if self.quantity is None:
            raise ValueError("Quantity must be provided")

        if self.product.stock < self.quantity:
            raise ValueError("There are no stock for this product.")

        self.unit_price = self.product.product_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} of {self.product}"
    
# Order model
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.ForeignKey(UserAddress, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=20, choices=[ # can change later
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered')
    ])
    total_amount = models.DecimalField(max_digits=50, decimal_places=2)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        total = sum([
            rel.product.product_price * rel.quantity
            for rel in self.orderdetailrelationship_set.all()
        ])
        self.total_amount = total

        super().save(update_fields=['total_amount'])
    def __str__(self):
        return f"Order #{self.id} by {self.user}"

# OrderDetail model    
class OrderDetailRelationship(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name}"