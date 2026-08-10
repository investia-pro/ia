"""
InvestIA PRO
Funções auxiliares

Versão: v0.6
Fase: 1.7

Responsável por:
- validação de dados de mercado;
- validação de indicadores;
- conversões seguras;
- formatação de valores;
- identificação de risco.
"""

from numbers import Number
from typing import Any

import math


# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

REQUIRED_INDICATORS = [
    "price",
    "rsi",
    "ma21",
    "ma200",
    "volatility",
]


# ==========================================================
# CONVERSÃO SEGURA
# ==========================================================

def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Converte um valor para float de forma segura.

    Retorna 'default' quando a conversão não é possível
    ou quando o resultado é NaN/infinito.
    """

    try:

        if value is None:
            return default

        result = float(value)

        if not math.isfinite(result):
            return default

        return result

    except (
        TypeError,
        ValueError,
    ):

        return default


# ==========================================================
# VALIDAÇÃO NUMÉRICA
# ==========================================================

def is_number(
    value: Any,
) -> bool:
    """
    Verifica se o valor é numérico, finito e válido.
    """

    if isinstance(
        value,
        bool,
    ):

        return False

    if not isinstance(
        value,
        Number,
    ):

        return False

    try:

        return math.isfinite(
            float(value)
        )

    except (
        TypeError,
        ValueError,
    ):

        return False


# ==========================================================
# VALIDAÇÃO DE DADOS DE MERCADO
# ==========================================================

def validate_market_data(
    data,
) -> bool:
    """
    Verifica se o DataFrame retornado possui dados válidos.
    """

    if data is None:
        return False

    try:

        if data.empty:
            return False

    except AttributeError:

        return False

    return True


# ==========================================================
# QUANTIDADE DE HISTÓRICO
# ==========================================================

def validate_history_length(
    data,
    minimum_rows: int = 200,
) -> bool:
    """
    Verifica se existe histórico suficiente para cálculos
    de indicadores de longo prazo.

    O padrão é 200 linhas, necessário para MA200.
    """

    if not validate_market_data(
        data
    ):

        return False

    try:

        return len(data) >= minimum_rows

    except (
        TypeError,
        AttributeError,
    ):

        return False


# ==========================================================
# VALIDAÇÃO DE COLUNAS DO MERCADO
# ==========================================================

def validate_market_columns(
    data,
) -> bool:
    """
    Verifica se o DataFrame possui as colunas fundamentais
    para análise de preço.
    """

    if not validate_market_data(
        data
    ):

        return False

    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    return all(
        column in data.columns
        for column in required_columns
    )


# ==========================================================
# VALIDAÇÃO DOS INDICADORES
# ==========================================================

def validate_indicators(
    data: dict,
) -> bool:
    """
    Valida os indicadores necessários para o Score InvestIA.

    Campos obrigatórios:

    price
    rsi
    ma21
    ma200
    volatility
    """

    if not isinstance(
        data,
        dict,
    ):

        return False

    # ------------------------------------------------------
    # Verifica existência dos campos
    # ------------------------------------------------------

    for field in REQUIRED_INDICATORS:

        if field not in data:

            return False

        if data[field] is None:

            return False

        if not is_number(
            data[field]
        ):

            return False

    # ------------------------------------------------------
    # Valores individuais
    # ------------------------------------------------------

    price = float(
        data["price"]
    )

    rsi = float(
        data["rsi"]
    )

    ma21 = float(
        data["ma21"]
    )

    ma200 = float(
        data["ma200"]
    )

    volatility = float(
        data["volatility"]
    )

    # ------------------------------------------------------
    # Preço
    # ------------------------------------------------------

    if price <= 0:

        return False

    # ------------------------------------------------------
    # Médias móveis
    # ------------------------------------------------------

    if ma21 <= 0:

        return False

    if ma200 <= 0:

        return False

    # ------------------------------------------------------
    # RSI
    # ------------------------------------------------------

    if not 0 <= rsi <= 100:

        return False

    # ------------------------------------------------------
    # Volatilidade
    # ------------------------------------------------------

    if volatility < 0:

        return False

    return True


# ==========================================================
# VALIDAÇÃO DA ANÁLISE
# ==========================================================

def validate_analysis_data(
    data: dict,
) -> bool:
    """
    Compatibilidade com a função existente na v0.5.3.

    Agora utiliza a validação completa dos indicadores.
    """

    return validate_indicators(
        data
    )


# ==========================================================
# VALIDAÇÃO COMPLETA
# ==========================================================

def validate_complete_analysis(
    market_data,
    indicators: dict,
    minimum_rows: int = 200,
) -> dict:
    """
    Executa uma validação completa antes da análise.

    Retorna:

    {
        "valid": True/False,
        "market_data": True/False,
        "history": True/False,
        "columns": True/False,
        "indicators": True/False,
        "errors": [...]
    }
    """

    errors = []

    market_valid = validate_market_data(
        market_data
    )

    if not market_valid:

        errors.append(
            "Dados de mercado inexistentes ou vazios."
        )

    columns_valid = validate_market_columns(
        market_data
    )

    if market_valid and not columns_valid:

        errors.append(
            "Colunas obrigatórias do mercado não encontradas."
        )

    history_valid = validate_history_length(
        market_data,
        minimum_rows,
    )

    if market_valid and not history_valid:

        errors.append(
            f"Histórico insuficiente. "
            f"Mínimo recomendado: {minimum_rows} registros."
        )

    indicators_valid = validate_indicators(
        indicators
    )

    if not indicators_valid:

        errors.append(
            "Indicadores técnicos inválidos ou incompletos."
        )

    valid = (
        market_valid
        and columns_valid
        and history_valid
        and indicators_valid
    )

    return {

        "valid": valid,

        "market_data": market_valid,

        "history": history_valid,

        "columns": columns_valid,

        "indicators": indicators_valid,

        "errors": errors,
    }


# ==========================================================
# FORMATAÇÃO MONETÁRIA
# ==========================================================

def format_currency(
    value,
) -> str:
    """
    Formata um número no padrão monetário brasileiro.
    """

    if value is None:

        return "N/A"

    try:

        value = float(value)

        if not math.isfinite(value):

            return "N/A"

    except (
        TypeError,
        ValueError,
    ):

        return "N/A"

    return (
        f"R$ {value:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


# ==========================================================
# FORMATAÇÃO DE PERCENTUAL
# ==========================================================

def format_percent(
    value,
) -> str:
    """
    Formata percentual.
    """

    if value is None:

        return "N/A"

    try:

        value = float(value)

        if not math.isfinite(value):

            return "N/A"

    except (
        TypeError,
        ValueError,
    ):

        return "N/A"

    return f"{value:.2f}%"


# ==========================================================
# ÍCONE DE RISCO
# ==========================================================

def risk_icon(
    risk: str,
) -> str:
    """
    Retorna o ícone correspondente ao nível de risco.
    """

    icons = {

        "Baixo": "🟢",

        "Moderado": "🟡",

        "Elevado": "🟠",

        "Alto": "🔴",

        "Muito Alto": "🔴",
    }

    return icons.get(
        risk,
        "⚪",
    )
