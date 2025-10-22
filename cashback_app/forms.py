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

class WalletReductionForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=0,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'مبلغ کسر از کیف پول (ریال)',
            'min': '1'
        }),
        label='مبلغ کسر'
    )
    reason = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'دلیل کسر از کیف پول'
        }),
        label='دلیل کسر'
    )
    
    def __init__(self, *args, customer=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.customer = customer
    
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if self.customer and amount > self.customer.wallet_balance:
            raise forms.ValidationError(
                f'مبلغ کسر نمی‌تواند بیشتر از موجودی کیف پول ({self.customer.wallet_balance:,} ریال) باشد.'
            )
        return amount