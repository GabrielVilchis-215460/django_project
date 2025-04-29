from pyexpat.errors import messages
from django.shortcuts import render, get_object_or_404, redirect
import stripe.error
# my models to work on
from .models import Product, Section, ShoppingCart, CartItem, UserAddress, Order, OrderDetailRelationship
# my forms to work on 
from .forms import ProductForm, CustomUserCreationFrom, CustomLoginForm, UserAddressForm, CustomUserUpdateForm
# import generic views that django provides
from django.views. generic import TemplateView, ListView, DetailView, View
# imports for log in and sign in
from django.contrib.auth import login as auth_login, get_user_model, logout as auth_logout, update_session_auth_hash, logout
from django.contrib.auth.decorators import login_required 
from django.db.models import Count
# imports for recover password
from django.core.mail import send_mail
import random
from django.contrib import messages
from django.conf import settings
import time
# imports for Stripe integrations
import stripe
from django.utils.decorators import method_decorator
from django.http import JsonResponse

User = get_user_model() # global variable for get the user data and model

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
# homepage view
class HomePage(TemplateView):
    template_name = 'home.html'
    # method to get the frst 4 products with stock to preorder products
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['preorder'] = Product.objects.filter(is_active=True)[:4]
        ctx['catalog'] = Product.objects.filter(is_active=True).order_by('?')[:4]
        #ctx['is_logged_in'] = self.request.user.is_authenticated
        return ctx

# CRUD OPERATIONS
# Read view
@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

# Create view
@login_required
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('read_product')
    else:
        form = ProductForm()

    return render(request, 'products_form.html', {'form' : form})
    
# Update view
@login_required
def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('read_product')
    else:
        form = ProductForm(instance=product)

    return render(request, 'products_form.html', {'form' : form})
    
# Delete view
@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('read_product')
    
    return render(request, 'products_delete.html', {'product' : product})

# login view
def login(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            # remember password management
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)

            # redirect by the user "type"   
            if user.is_staff:
                return redirect('read_product') 
            else:
                return redirect('home')            
    else:
        form = CustomLoginForm()
        
    return render(request, 'login.html', {'form':form})

# signin view
def signin(request):
    if request.method == 'POST':
        form =  CustomUserCreationFrom(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationFrom()

    return render(request, 'signin.html', {'form': form})

# logut view
def logout_view(request):
    auth_logout(request)
    return redirect('home')

# catalog view
class CatalogView(ListView):
    model = Product
    template_name = 'catalog.html'
    paginate_by = 12

    # method to get the products with stock
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        
        platform = self.request.GET.get('platform')
        supplier = self.request.GET.get('supplier')
        category = self.request.GET.get('category')
        # search bar
        search_query = self.request.GET.get('search')

        if platform:
            queryset = queryset.filter(platform=platform)
        
        if supplier:
            queryset = queryset.filter(supplier=supplier)
        
        if category:
            queryset = queryset.filter(section__category=category)
        if search_query:
            queryset = queryset.filter(product_name__icontains=search_query)

        #return queryset.order_by('?') # random produtcs
        return queryset.order_by('id')
    
    # method to get products grouped by categories, suppliers and platofrms
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categories'] = Section.objects.annotate(count=Count('product')).filter(count__gt=0)
        context['platforms'] = Product.objects.values_list('platform', flat=True).distinct()
        context['suppliers'] = Product.objects.values_list('supplier', flat=True).distinct()

        return context

# Product detail view
class ProductView(DetailView):
    model = Product
    template_name = 'product_view.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['catalog'] = Product.objects.filter(is_active=True).order_by('?')[:4]
        return ctx

# Shopping cart view
@login_required
def ShoppingCartView(request):
    cart, created_cart = ShoppingCart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total = sum(item.unit_price * item.quantity for item in cart_items)

    # user address management
    try:
        user_address = UserAddress.objects.get(user=request.user)
    except UserAddress.DoesNotExist:
        user_address = None

    if request.method == 'POST':
        if user_address:
            form = UserAddressForm(request.POST, instance=user_address)
        else:
            form = UserAddressForm(request.POST)
        
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
    else:
        if user_address:
            form = UserAddressForm(instance=user_address)
        else:
            form = UserAddressForm()

    return render(request, 'shopping_cart.html', {'cart_items':cart_items, 'total':total, 'form':form})

# add products to cart
@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart, created = ShoppingCart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    # if the item is created on the card
    if created:
        item.quantity = 1
    else:
        item.quantity += 1
    item.save()

    return redirect('shopping_cart')

# this if quantity form in product view in the future
def update_cart_item(request, item_id):
     item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
 
     if request.method == 'POST':
        try:
            new_qty = int(request.POST.get('quantity'))

            if new_qty < 1:
                item.delete()
            elif new_qty > item.product.stock:        
                item.quantity = item.product.stock
                item.save()
            else:
                item.quantity = new_qty
                item.save()
        except (ValueError, TypeError):
            pass
            
     return redirect('shopping_cart')

# delete products to cart
@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect ('shopping_cart')

# increase and decrement quantity
@login_required
def increment_cart_item(request, item_id):
    if request.method == 'POST':
        item  = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
        if item.quantity < item.product.stock:
            item.quantity += 1
            item.save()

        return JsonResponse({'success': True, 'quantity': item.quantity})  
      
    return JsonResponse({'success': False})

@login_required
def decrement_cart_item(request, item_id):
    if request.method == 'POST':
        item =get_object_or_404(CartItem, id=item_id, cart__user=request.user)

        if item.quantity > 1:
            item.quantity -= 1
            item.save()
            return JsonResponse({'success': True, 'quantity': item.quantity})
        else:
            item.delete()
            return JsonResponse({'success': True, 'quantity': 0}) 
        
    return JsonResponse({'success': False})

# user profile view
@login_required
def user_profile(request):

    user = request.user
    section = request.GET.get('section', 'profile')
    user_form = CustomUserUpdateForm(instance=user)
    address = UserAddress.objects.filter(user=user).first()
    
    if not address:
        address = UserAddress(user=user)
    address_form = UserAddressForm(instance=address)

    if request.method == 'POST':
        user_form = CustomUserUpdateForm(request.POST, instance=user)
        address_form = UserAddressForm(request.POST, instance=address)

        if user_form.is_valid() and address_form.is_valid():
            user_form.save()
            address_form.save()
            messages.success(request, "Profile updated successfully!")
            
            return redirect('user_dashboard')

    ctx = {
        'user_form': user_form,
        'section': section,
        'address_form': address_form
    }

    if section == 'orders':
        orders = Order.objects.filter(user=user)
        print(f"Pedidos encontrados: {orders.count()}") 
        ctx['orders'] = orders

    return render(request, 'user_profile.html', ctx)

# verify code to change password view
def verify_code(request):
    # the setps are going to be:
    # -request email
    # -verify code
    # -change change password
    step = request.session.get('reset_step','request')

    if request.method == 'POST':
       try:
            # first step is request user email address
        if step == 'request':
            email = request.POST.get('email')

            try:
                usr = User.objects.get(email=email)
                verification_code = random.randint(100000, 999999)
                request.session['reset_email'] = usr.email
                request.session['verification_code'] = str(verification_code)
                request.session['reset_step'] = 'verify'
                request.session['code_timestamp'] = time.time()

                # send the code via email address
                send_mail(
                    subject='Your verification code',
                    message=f'Your verification code is: {verification_code}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[usr.email],
                    fail_silently=False,
                )
                messages.success(request, "Code send to your email.")
                return redirect('password_reset')
            
            except usr.DoesNotExist:
                messages.error(request, "There's no user with this email.")
        # second step is verify the verfication code
        elif step=='verify':
            entered_code = request.POST.get('code')
            session_code = request.session.get('verification_code')
            code_timestamp = request.session.get('code_timestamp')

            current_time = time.time()

            if code_timestamp and (current_time - code_timestamp > 5 * 60):
                # expired code
                messages.error(request, "The verification code has expired. Please request a new one.")
                request.session.pop('reset_email', None)
                request.session.pop('verification_code', None)
                request.session.pop('code_timestamp', None)
                request.session['reset_step'] = 'request'
                return redirect('password_reset')

            if entered_code == session_code:
                request.session['reset_step'] = 'change'
                return redirect('password_reset')
            else:
                messages.error(request, "Wrong code, please try again.")
        # thrid step is change password
        elif step == 'change':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if new_password == confirm_password:
                try:
                    email = request.session.get('reset_email')
                    usr = User.objects.get(email=email)
                    usr.set_password(new_password)
                    usr.save()
                    update_session_auth_hash(request, usr)
                    # close users session after the change
                    logout(request)
                    # clean the session
                    request.session.pop('reset_email', None)
                    request.session.pop('verification_code', None)
                    request.session.pop('code_timestamp', None)
                    request.session.pop('reset_step', None)
                    messages.success(request, "The password has been changed succesfully!")
                    return redirect('login')
                
                except usr.DoesNotExist:
                    messages.error(request,"Error to change password.")
        else:
            messages.error(request, "Passwords doesn't are the same")
       except Exception as e:
           messages.error(request, f"Error: {str(e)}")

    return render(request, 'change_password.html', {'step':step})


# checkout view with stripe
class CheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        cart = ShoppingCart.objects.get(user=request.user)
        cart_item = CartItem.objects.filter(cart=cart)

        if not cart_item.exists():
            return redirect('catalog')

        line_items = []
        for item in cart_item:
            line_items.append({
                'price_data':{
                        'currency': 'mxn',
                        'product_data':{
                            'name': item.product.product_name,
                        },
                        'unit_amount': int(item.unit_price * 100),
                    },
                    'quantity': item.quantity,
            })

        checkout = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url='http://localhost:8000/success/',
            cancel_url='http://localhost:8000/cancel/',
        )

        return redirect(checkout.url)

# view for get order history
#@method_decorator(login_required(login_url='login'), name='dispatch')
class SuccessView(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        try:
            cart, created_cart = ShoppingCart.objects.get_or_create(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)

            if not cart_items.exists():
                return redirect('cancel')

            address = UserAddress.objects.filter(user=request.user).first()
            if not address:
                return redirect('cancel')

            # validate stock 
            for item in cart_items:
                if item.product.stock < item.quantity:
                    return render(request, 'cancel.html')
            #total = sum(item.unit_price * item.quantity for item in cart_items)

            order = Order.objects.create(
                user=request.user,
                address=address,
                order_status='pending',
                total_amount=0.00,
            )

            for item in cart_items:
                OrderDetailRelationship.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                )

                item.product.stock -= item.quantity
                item.product.save()
            # update total amount of the order
            order.save()

            # delete cart items after the pay
            cart_items.delete()

            return render(request, 'success.html')

        except ShoppingCart.DoesNotExist:
            return redirect('catalog')

# cancel view
class CancelView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'cancel.html')