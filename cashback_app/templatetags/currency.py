from django import template

register = template.Library()


@register.filter(name='price')
def price(value):
    """
    Format numeric values with thousands separators for currency display.
    Usage: {{ amount|price }} -> e.g., 1,234,567
    Handles None gracefully (returns 0).
    """
    if value is None or value == '':
        return '0'
    try:
        # Try to convert to int for clean formatting (Decimals are integer-based in this app)
        ivalue = int(value)
        return f"{ivalue:,}"
    except (ValueError, TypeError):
        try:
            # Fallback: format as float with no decimals then add separators
            fvalue = float(value)
            return f"{int(round(fvalue)):,}"
        except Exception:
            # If all else fails, return original value as string
            return str(value)

