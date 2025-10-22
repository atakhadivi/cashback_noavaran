from django.contrib import admin
from .models import Customer, Purchase, ActivityLog
import jdatetime
from django.utils import timezone
import pytz


class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'national_code', 'phone_number', 'wallet_balance', 'formatted_created_at', 'formatted_updated_at']
    search_fields = ['first_name', 'last_name', 'national_code', 'phone_number']
    list_filter = ['created_at']

    def formatted_created_at(self, obj):
        if obj.created_at:
            jdate = jdatetime.datetime.fromgregorian(datetime=obj.created_at)
            return jdate.strftime('%Y/%m/%d %H:%M')
        return '-'
    formatted_created_at.short_description = 'تاریخ ثبت'
    formatted_created_at.admin_order_field = 'created_at'

    def formatted_updated_at(self, obj):
        if obj.updated_at:
            jdate = jdatetime.datetime.fromgregorian(datetime=obj.updated_at)
            return jdate.strftime('%Y/%m/%d %H:%M')
        return '-'
    formatted_updated_at.short_description = 'تاریخ بروزرسانی'
    formatted_updated_at.admin_order_field = 'updated_at'


class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['customer', 'amount', 'cashback_amount', 'formatted_created_at']
    list_filter = ['created_at', 'customer']
    search_fields = ['customer__first_name', 'customer__last_name', 'customer__national_code']

    def formatted_created_at(self, obj):
        if obj.created_at:
            jdate = jdatetime.datetime.fromgregorian(datetime=obj.created_at)
            return jdate.strftime('%Y/%m/%d %H:%M')
        return '-'
    formatted_created_at.short_description = 'تاریخ ثبت'
    formatted_created_at.admin_order_field = 'created_at'


class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'customer', 'description', 'ip_address', 'formatted_created_at']
    list_filter = ['activity_type', 'created_at', 'user']
    search_fields = ['user__username', 'description', 'customer__first_name', 'customer__last_name', 'customer__national_code']
    readonly_fields = ['user', 'activity_type', 'customer', 'description', 'ip_address', 'created_at']
    ordering = ['-created_at']
    
    def formatted_created_at(self, obj):
        if obj.created_at:
            # Convert to Tehran timezone
            tehran_tz = pytz.timezone('Asia/Tehran')
            if timezone.is_aware(obj.created_at):
                local_time = obj.created_at.astimezone(tehran_tz)
            else:
                local_time = obj.created_at
            jdate = jdatetime.datetime.fromgregorian(datetime=local_time)
            return jdate.strftime('%Y/%m/%d %H:%M:%S')
        return '-'
    formatted_created_at.short_description = 'تاریخ و زمان'
    formatted_created_at.admin_order_field = 'created_at'
    
    def has_add_permission(self, request):
        # Prevent manual addition of activity logs
        return False
    
    def has_change_permission(self, request, obj=None):
        # Prevent editing of activity logs
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Allow deletion for cleanup purposes
        return request.user.is_superuser


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(ActivityLog, ActivityLogAdmin)