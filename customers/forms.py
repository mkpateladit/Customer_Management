import re

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Customer


class CustomerForm(forms.ModelForm):
    """Used for both Add and Update. Field-level validation lives in the
    clean_<field> methods below, in addition to the model-level validators."""

    class Meta:
        model = Customer
        fields = [
            'name', 'email', 'phone', 'company_name',
            'address_line', 'city', 'state', 'pincode',
            'gst_number', 'status', 'notes',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Rajesh Traders'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+919812345678'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Business / shop name'}),
            'address_line': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street, area'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '380001'}),
            'gst_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional internal notes'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 3:
            raise forms.ValidationError("Name must be at least 3 characters long.")
        if not re.match(r'^[A-Za-z0-9\s\.\-&,]+$', name):
            raise forms.ValidationError("Name contains invalid characters.")
        return name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not re.match(r'^\+?\d{9,15}$', phone):
            raise forms.ValidationError("Enter a valid phone number (9-15 digits, optional leading '+').")
        return phone

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode', '').strip()
        if pincode and not re.match(r'^\d{4,10}$', pincode):
            raise forms.ValidationError("Pincode must be 4 to 10 digits.")
        return pincode

    def clean_email(self):
        # EmailField already validates format; this just normalises case.
        return self.cleaned_data.get('email', '').strip().lower()


class DistributorRegisterForm(UserCreationForm):
    """Self-service signup form for new Distributor accounts."""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'})
    )
    phone = forms.CharField(
        required=False, max_length=17,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+919812345678'})
    )
    company_name = forms.CharField(
        required=False, max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your distribution business name'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Choose a username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm password'})

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile = user.profile
            profile.role = 'distributor'
            profile.phone = self.cleaned_data.get('phone', '')
            profile.company_name = self.cleaned_data.get('company_name', '')
            profile.save()
        return user
