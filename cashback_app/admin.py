from django.contrib import admin
from .models import Customer, Purchase
import jdatetime


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


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Purchase, PurchaseAdmin)