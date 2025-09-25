from django import forms
from .models import Customer, Purchase

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'national_code', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام خانوادگی'}),
            'national_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'کد ملی - 10 رقم'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شماره موبایل - مثال: 09123456789'}),
        }

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['customer', 'amount']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مبلغ خرید (ریال)'}),
        }