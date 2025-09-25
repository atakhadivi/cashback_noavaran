from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User, Group
from .models import UserProfile

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام کاربری'}),
        label='نام کاربری'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'رمز عبور'}),
        label='رمز عبور'
    )

class OperatorCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام'}),
        label='نام'
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام خانوادگی'}),
        label='نام خانوادگی'
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ایمیل'}),
        label='ایمیل'
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super(OperatorCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'نام کاربری'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'رمز عبور'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'تکرار رمز عبور'})
        
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Create operator profile
            UserProfile.objects.create(user=user, user_type='operator')
            # Add to operator group
            operator_group, created = Group.objects.get_or_create(name='Operator')
            user.groups.add(operator_group)
        return user