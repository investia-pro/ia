"""
InvestIA PRO
Funções auxiliares

Versão: 0.5.3 Stable
"""

from numbers import Number


def validate_market_data(data):
    """
    Verifica se o DataFrame retornado possui dados.
    """
    return data is not None and not data.empty


def validate_analysis_data(data):
    """
    Valida os campos necessários para análise.
    """

    required = [
        "price",
        "rsi",
        "ma21",
        "ma200",
        "volatility",
    ]

    return all(
        field in data and data[field] is not None
        for field in required
    )


def safe_float(value, default=0.0):
    """
    Converte um valor para float de forma segura.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def format_currency(value):
    """
    Formata um número no padrão monetário brasileiro.
    """

    if value is None:
        return "N/A"

    value = safe_float(value)

    return (
        f"R$ {value:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def format_percent(value):
    """
    Formata percentual.
    """

    if value is None:
        return "N/A"

    value = safe_float(value)

    return f"{value:.2f}%"


def risk_icon(risk):
    """
    Ícone correspondente ao risco.
    """

    icons = {
        "Baixo": "🟢",
        "Moderado": "🟡",
        "Alto": "🔴",
    }

    return icons.get(risk, "⚪")


def is_number(value):
    """
    Verifica se o valor é numérico.
    """

    return isinstance(value, Number)
