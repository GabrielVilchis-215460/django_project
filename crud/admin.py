from django.contrib import admin
from .models import Product, Section, CustomUser,ShoppingCart,CartItem,Order,OrderDetailRelationship
from django.contrib.auth.admin import UserAdmin

# Register your models here.
admin.site.register(Product)
admin.site.register(Section)
admin.site.register(ShoppingCart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderDetailRelationship)
# For the administrator
class CustomAdmin(UserAdmin):
    model = CustomUser
    list_display = [
        'username', 'first_name', 'last_name', 'email', 
        'is_staff', 'is_superuser'
    ]
    fieldsets = UserAdmin.fieldsets + (
        ('Aditional information', {'fields': ('phone_number',)}),
    )

admin.site.register(CustomUser, CustomAdmin)