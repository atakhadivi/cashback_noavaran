from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
import re

class Customer(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="نام")
    last_name = models.CharField(max_length=100, verbose_name="نام خانوادگی")
    national_code = models.CharField(
        max_length=10, 
        unique=True, 
        verbose_name="کد ملی",
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="کد ملی باید دقیقاً 10 رقم باشد",
            ),
        ]
    )
    phone_number = models.CharField(
        max_length=11, 
        verbose_name="شماره موبایل",
        validators=[
            RegexValidator(
                regex=r'^09\d{9}$',
                message="شماره موبایل باید با 09 شروع شود و 11 رقم باشد",
            ),
        ]
    )
    wallet_balance = models.DecimalField(
        max_digits=12, 
        decimal_places=0, 
        default=0, 
        verbose_name="موجودی کیف پول"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.national_code}"
    
    def save(self, *args, **kwargs):
        # Validate national code
        if not self.is_valid_national_code(self.national_code):
            from django.core.exceptions import ValidationError
            raise ValidationError("کد ملی وارد شده معتبر نیست")
        super().save(*args, **kwargs)
    
    @staticmethod
    def is_valid_national_code(national_code):
        if not re.match(r'^\d{10}$', national_code):
            return False
        
        # Check if all digits are the same
        if len(set(national_code)) == 1:
            return False
        
        # Iranian National Code validation algorithm
        check = int(national_code[9])
        s = sum(int(national_code[i]) * (10 - i) for i in range(9)) % 11
        return (s < 2 and check == s) or (s >= 2 and check == 11 - s)
    
    class Meta:
        verbose_name = "مشتری"
        verbose_name_plural = "مشتریان"


class Purchase(models.Model):
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='purchases',
        verbose_name="مشتری"
    )
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=0, 
        verbose_name="مبلغ خرید"
    )
    cashback_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=0, 
        verbose_name="مبلغ کش‌بک"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="ثبت کننده"
    )

    def save(self, *args, **kwargs):
        from decimal import Decimal
        # Calculate cashback (5% of purchase amount)
        if not self.cashback_amount:
            self.cashback_amount = self.amount * Decimal('0.05')
        
        # Add cashback to customer wallet
        self.customer.wallet_balance += self.cashback_amount
        self.customer.save()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.customer} - {self.amount} - {self.created_at.strftime('%Y-%m-%d')}"
    
    class Meta:
        verbose_name = "خرید"
        verbose_name_plural = "خریدها"
        ordering = ['-created_at']


class ActivityLog(models.Model):
    ACTIVITY_TYPES = (
        ('customer_create', 'ثبت مشتری'),
        ('customer_edit', 'ویرایش مشتری'),
        ('purchase_create', 'ثبت خرید'),
        ('user_login', 'ورود به سیستم'),
        ('user_logout', 'خروج از سیستم'),
    )
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="کاربر"
    )
    activity_type = models.CharField(
        max_length=20, 
        choices=ACTIVITY_TYPES,
        verbose_name="نوع فعالیت"
    )
    description = models.TextField(verbose_name="توضیحات")
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True,
        verbose_name="آدرس IP"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        verbose_name = "گزارش فعالیت"
        verbose_name_plural = "گزارش فعالیت‌ها"
        ordering = ['-created_at']


class UserProfile(models.Model):
    USER_TYPES = (
        ('admin', 'مدیر'),
        ('operator', 'اپراتور'),
    )
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        verbose_name="کاربر"
    )
    user_type = models.CharField(
        max_length=10, 
        choices=USER_TYPES,
        default='operator',
        verbose_name="نوع کاربر"
    )
    
    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"
    
    class Meta:
        verbose_name = "پروفایل کاربر"
        verbose_name_plural = "پروفایل کاربران"