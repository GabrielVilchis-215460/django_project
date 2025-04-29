from django.urls import path
from . import views
from .views import ProductView, CheckoutSessionView, SuccessView, CancelView

urlpatterns = [
    path('', views.HomePage.as_view(), name='home'),
    # crud operations
    path('catalog', views.CatalogView.as_view(), name='catalog'),
    path('read/', views.product_list, name='read_product'),
    path('new/', views.create_product, name='create_product'),
    path('update/<int:pk>/', views.update_product, name='update_product'),
    path('delete/<int:pk>/', views.delete_product, name='delete_product'),
    # user auth operations
    path('login/', views.login, name='login'),
    path('signin/', views.signin, name='signin'),
    path('logout/', views.logout_view, name='logout-user'),
    path('product/<int:pk>', ProductView.as_view(), name='product_detail'),
    # shopping card operations
    path('shopping-cart/', views.ShoppingCartView, name='shopping_cart'),
    path('shopping-cart/add/<int:pk>', views.add_to_cart, name='add_to_cart'),
    path('shopping-cart/remove/<int:item_id>', views.remove_from_cart, name='remove_from_cart'),
    path('shoping-cart/update/<int:item_id>', views.update_cart_item, name='update_cart'),
    path('shopping-cart/increment/<int:item_id>/', views.increment_cart_item, name='increase-qty'),
    path('shopping-cart/decrease/<int:item_id>/', views.decrement_cart_item, name='decrease-qty'),
    # user profile operations
    path('profile/', views.user_profile, name="user_dashboard"),
    # change password
    path('change-password/', views.verify_code, name='password_reset'),
    # checkout 
    path('checkout/', CheckoutSessionView.as_view(), name='checkout'),
    path('success/', SuccessView.as_view(), name='success'),
    path('cancel/', CancelView.as_view(), name='cancel')
]