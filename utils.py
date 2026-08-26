"""
InvestIA PRO - Funções Utilitárias e Padronização de Formatação
"""
import datetime

def format_ticker(ticker: str) -> str:
    """Padroniza o ticker para inclusão do sufixo .SA caso seja brasileiro e não contenha ponto."""
    if not ticker:
        return ""
    clean_ticker = ticker.strip().upper()
    if not "." in clean_ticker:
        return f"{clean_ticker}.SA"
    return clean_ticker

def format_currency(val: float) -> str:
    """Formata valor numérico para Moeda Brasileira (R$)."""
    if val is None or val != val:
        return "N/D"
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_percent(val: float) -> str:
    """Formata valor numérico para Porcentagem (%)."""
    if val is None or val != val:
        return "N/D"
    return f"{val:+.2f}%".replace(".", ",")

def safe_get(dictionary, keys, default=None):
    """Navegação segura em dicionários aninhados para evitar KeyError."""
    curr = dictionary
    for k in keys:
        if isinstance(curr, dict) and k in curr:
            curr = curr[k]
        else:
            return default
    return curr
