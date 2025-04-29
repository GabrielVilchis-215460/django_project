from django import forms
from .models import Product, CustomUser, UserAddress
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

class CustomUserCreationFrom(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(
        max_length=10, 
        required=True,
        validators=[
            RegexValidator(r'^\d{10}$', message="The phone number must have exactly 10 digits.")
        ]
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'phone_number')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address already is already registered.')
        return email

class CustomLoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, label='remember')

class UserAddressForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = {'address', 'city', 'zip_code','country','state'}

        def clean_zipCode(self):
            zid_code =  self.cleaned_data.get('zip_code')
            if not zid_code.isdigit():
                raise forms.ValidationError('The zip code must contains only numbers,')
            if len(zid_code) not in [5,6]:
                raise forms.ValidationError('The zip code must contain 5 or 6 digits.')
            return zid_code

class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_id = self.instance.id
        if CustomUser.objects.exclude(id=user_id).filter(email=email).explain():
            raise forms.ValidationError('This email address is already registered by other user. ')
        return email
    
    def clean_phoneNumber(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit():
            raise forms.ValidationError('The phone number must contains only numbers.')
        if len(phone_number) != 10:
            raise forms.ValidationError('The phone number must contains exactly 10 digits.')
        return phone_number