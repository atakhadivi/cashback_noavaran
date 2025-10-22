from django import template
from django.utils import timezone
import jdatetime
import pytz

register = template.Library()

@register.filter
def persian_date(value):
    if value is None:
        return ''
    # Convert to Tehran timezone if it's a timezone-aware datetime
    if hasattr(value, 'tzinfo') and value.tzinfo is not None:
        tehran_tz = pytz.timezone('Asia/Tehran')
        value = value.astimezone(tehran_tz)
    jalali_date = jdatetime.date.fromgregorian(date=value)
    return jalali_date.strftime('%Y/%m/%d')

@register.filter
def persian_datetime(value):
    if value is None:
        return ''
    # Convert to Tehran timezone if it's a timezone-aware datetime
    if hasattr(value, 'tzinfo') and value.tzinfo is not None:
        tehran_tz = pytz.timezone('Asia/Tehran')
        value = value.astimezone(tehran_tz)
    jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
    return jalali_date.strftime('%Y/%m/%d %H:%M:%S')