"""InvestIA PRO - Utilitários | Versão Final 3.1.3"""
import math

def safe_float(value, default=None):
    try:
        if value is None or isinstance(value,bool): return default
        value=float(value)
        return value if math.isfinite(value) else default
    except (TypeError,ValueError): return default

def safe_int(value, default=None):
    value=safe_float(value)
    return default if value is None else int(value)

def clamp(value, minimum=0, maximum=100):
    value=safe_float(value, minimum)
    return max(minimum,min(maximum,value))

def normalize_percent(value, default=None):
    value=safe_float(value, default)
    if value is None:return default
    return value*100 if abs(value)<=1 else value

def format_currency(value):
    value=safe_float(value)
    if value is None:return "N/D"
    return "R$ "+f"{value:,.2f}".replace(",","X").replace(".",",").replace("X",".")

def format_number(value, decimals=2):
    value=safe_float(value)
    if value is None:return "N/D"
    return f"{value:,.{decimals}f}".replace(",","X").replace(".",",").replace("X",".")

def format_percent(value, decimals=2):
    value=normalize_percent(value)
    return "N/D" if value is None else format_number(value,decimals)+"%"
