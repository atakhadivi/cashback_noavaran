from django import template
import jdatetime

register = template.Library()

@register.filter
def persian_date(value):
    if value is None:
        return ''
    jalali_date = jdatetime.date.fromgregorian(date=value)
    return jalali_date.strftime('%Y/%m/%d')

@register.filter
def persian_datetime(value):
    if value is None:
        return ''
    jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
    return jalali_date.strftime('%Y/%m/%d %H:%M:%S')