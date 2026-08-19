"""
InvestIA PRO
Funções utilitárias

Versão: v0.6
Fase: 2.9.6 - Estabilidade e Validação de Dados
"""

import math


# ==========================================================
# VALIDAÇÃO NUMÉRICA
# ==========================================================

def is_valid_number(value):
    """
    Verifica se um valor é numérico e válido.

    Retorna:
        True  -> número válido
        False -> None, NaN, infinito ou não numérico
    """

    if value is None:
        return False

    try:

        number = float(value)

    except (
        TypeError,
        ValueError,
    ):

        return False

    return math.isfinite(number)


# ==========================================================
# CONVERSÃO SEGURA
# ==========================================================

def safe_float(
    value,
    default=None,
):
    """
    Converte um valor para float com segurança.

    Valores inválidos retornam o default.
    """

    if not is_valid_number(value):
        return default

    try:

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return default


# ==========================================================
# VALIDAÇÃO DOS INDICADORES
# ==========================================================

def validate_indicator(
    name,
    value,
):
    """
    Valida individualmente um indicador.

    Retorna um dicionário padronizado.
    """

    if not is_valid_number(value):

        return {
            "name": name,
            "valid": False,
            "value": None,
            "status": "INVALIDO",
            "message":
                f"{name} não possui um valor numérico válido.",
        }

    numeric_value = float(value)

    return {
        "name": name,
        "valid": True,
        "value": numeric_value,
        "status": "VALIDO",
        "message":
            f"{name} válido.",
    }


# ==========================================================
# VALIDAÇÃO COMPLETA DOS INDICADORES
# ==========================================================

def validate_indicators(
    data,
):
    """
    Valida os principais indicadores utilizados
    pelo InvestIA PRO.

    Indicadores obrigatórios:

        price
        ma21
        ma200
        rsi

    Volatilidade é tratada como indicador adicional.
    """

    if not isinstance(
        data,
        dict,
    ):

        return {
            "valid": False,
            "status": "INCONSISTENTE",
            "status_icon": "🔴",
            "message":
                "Os dados dos indicadores não estão "
                "em formato válido.",
            "indicators": {},
            "missing": [],
            "invalid": [],
        }

    required = [
        "price",
        "ma21",
        "ma200",
        "rsi",
    ]

    optional = [
        "volatility",
    ]

    indicator_results = {}

    missing = []

    invalid = []

    # ======================================================
    # INDICADORES OBRIGATÓRIOS
    # ======================================================

    for name in required:

        if name not in data:

            missing.append(
                name
            )

            indicator_results[name] = {
                "name": name,
                "valid": False,
                "value": None,
                "status": "AUSENTE",
                "message":
                    f"{name} não foi encontrado.",
            }

            continue

        result = validate_indicator(
            name,
            data.get(name),
        )

        indicator_results[name] = result

        if not result["valid"]:

            invalid.append(
                name
            )

    # ======================================================
    # INDICADORES OPCIONAIS
    # ======================================================

    for name in optional:

        if name not in data:

            indicator_results[name] = {
                "name": name,
                "valid": False,
                "value": None,
                "status": "AUSENTE",
                "message":
                    f"{name} não foi informado.",
            }

            continue

        result = validate_indicator(
            name,
            data.get(name),
        )

        indicator_results[name] = result

    # ======================================================
    # STATUS
    # ======================================================

    if missing or invalid:

        if missing:

            status = "INCOMPLETO"
            status_icon = "🟡"

            message = (
                "Existem dados obrigatórios ausentes: "
                + ", ".join(missing)
                + "."
            )

        else:

            status = "INCONSISTENTE"
            status_icon = "🔴"

            message = (
                "Existem indicadores com valores inválidos: "
                + ", ".join(invalid)
                + "."
            )

        valid = False

    else:

        status = "CONSISTENTE"
        status_icon = "🟢"

        message = (
            "Todos os indicadores obrigatórios "
            "estão válidos."
        )

        valid = True

    return {

        "valid": valid,

        "status": status,

        "status_icon": status_icon,

        "message": message,

        "indicators": indicator_results,

        "missing": missing,

        "invalid": invalid,
    }


# ==========================================================
# VALIDAÇÃO DOS DADOS PARA ANÁLISE
# ==========================================================

def validate_analysis_data(
    data,
):
    """
    Valida os dados necessários para o motor
    de análise do InvestIA PRO.

    Retorna True somente quando os indicadores
    obrigatórios possuem valores válidos.
    """

    result = validate_indicators(
        data
    )

    return result["valid"]


# ==========================================================
# DIAGNÓSTICO DOS DADOS
# ==========================================================

def get_data_diagnostics(
    data,
):
    """
    Retorna diagnóstico detalhado dos dados.

    Útil para debugging e para apresentação
    no Dashboard.
    """

    validation = validate_indicators(
        data
    )

    diagnostics = []

    for name, item in validation[
        "indicators"
    ].items():

        diagnostics.append({

            "indicator": name,

            "valid": item.get(
                "valid",
                False,
            ),

            "status": item.get(
                "status",
                "DESCONHECIDO",
            ),

            "value": item.get(
                "value"
            ),

            "message": item.get(
                "message",
                "",
            ),
        })

    return {

        "valid":
            validation["valid"],

        "status":
            validation["status"],

        "status_icon":
            validation["status_icon"],

        "message":
            validation["message"],

        "diagnostics":
            diagnostics,

        "missing":
            validation["missing"],

        "invalid":
            validation["invalid"],
    }


# ==========================================================
# VALIDAÇÃO DE PREÇO
# ==========================================================

def validate_price(
    price,
):
    """
    Valida especificamente o preço do ativo.
    """

    if not is_valid_number(price):

        return False

    price = float(price)

    return price > 0


# ==========================================================
# VALIDAÇÃO DO RSI
# ==========================================================

def validate_rsi(
    rsi,
):
    """
    Valida o RSI.

    O RSI deve estar entre 0 e 100.
    """

    if not is_valid_number(rsi):

        return False

    rsi = float(rsi)

    return 0 <= rsi <= 100


# ==========================================================
# VALIDAÇÃO DA VOLATILIDADE
# ==========================================================

def validate_volatility(
    volatility,
):
    """
    Valida a volatilidade.

    A volatilidade não pode ser negativa.
    """

    if not is_valid_number(
        volatility
    ):

        return False

    volatility = float(
        volatility
    )

    return volatility >= 0


# ==========================================================
# VALIDAÇÃO AVANÇADA
# ==========================================================

def validate_analysis_values(
    data,
):
    """
    Validação complementar dos valores.

    Além de verificar se são numéricos,
    verifica limites financeiros conhecidos.
    """

    if not isinstance(
        data,
        dict,
    ):

        return {

            "valid": False,

            "errors": [
                "Dados inválidos."
            ],
        }

    errors = []

    # ------------------------------------------------------
    # PREÇO
    # ------------------------------------------------------

    if "price" in data:

        if not validate_price(
            data["price"]
        ):

            errors.append(
                "Preço inválido."
            )

    else:

        errors.append(
            "Preço não informado."
        )

    # ------------------------------------------------------
    # MA21
    # ------------------------------------------------------

    if "ma21" not in data:

        errors.append(
            "MA21 não informada."
        )

    elif not is_valid_number(
        data["ma21"]
    ):

        errors.append(
            "MA21 inválida."
        )

    # ------------------------------------------------------
    # MA200
    # ------------------------------------------------------

    if "ma200" not in data:

        errors.append(
            "MA200 não informada."
        )

    elif not is_valid_number(
        data["ma200"]
    ):

        errors.append(
            "MA200 inválida."
        )

    # ------------------------------------------------------
    # RSI
    # ------------------------------------------------------

    if "rsi" not in data:

        errors.append(
            "RSI não informado."
        )

    elif not validate_rsi(
        data["rsi"]
    ):

        errors.append(
            "RSI inválido. "
            "O valor deve estar entre 0 e 100."
        )

    # ------------------------------------------------------
    # VOLATILIDADE
    # ------------------------------------------------------

    if "volatility" in data:

        if not validate_volatility(
            data["volatility"]
        ):

            errors.append(
                "Volatilidade inválida."
            )

    # ------------------------------------------------------
    # RETORNO
    # ------------------------------------------------------

    return {

        "valid":
            len(errors) == 0,

        "errors":
            errors,
    }


# ==========================================================
# FORMATAÇÃO DE MOEDA
# ==========================================================

def format_currency(
    value,
):
    """
    Formata valor no padrão monetário brasileiro.

    Exemplo:

        40.87
        ->
        R$ 40,87
    """

    if not is_valid_number(
        value
    ):

        return "N/D"

    try:

        value = float(value)

    except (
        TypeError,
        ValueError,
    ):

        return "N/D"

    formatted = (
        f"{value:,.2f}"
        .replace(
            ",",
            "X",
        )
        .replace(
            ".",
            ",",
        )
        .replace(
            "X",
            ".",
        )
    )

    return f"R$ {formatted}"


# ==========================================================
# FORMATAÇÃO PERCENTUAL
# ==========================================================

def format_percent(
    value,
    decimals=2,
):
    """
    Formata percentual.
    """

    if not is_valid_number(
        value
    ):

        return "N/D"

    try:

        return (
            f"{float(value):.{decimals}f}%"
        )

    except (
        TypeError,
        ValueError,
    ):

        return "N/D"


# ==========================================================
# ÍCONE DE RISCO
# ==========================================================

def risk_icon(
    risk,
):
    """
    Retorna um ícone conforme o nível de risco.
    """

    if risk is None:

        return "⚪"

    risk_text = str(
        risk
    ).strip().upper()

    if (
        "ALTO" in risk_text
        or "ELEVADO" in risk_text
    ):

        return "🔴"

    if (
        "MODERADO" in risk_text
        or "MÉDIO" in risk_text
        or "MEDIO" in risk_text
    ):

        return "🟡"

    if (
        "BAIXO" in risk_text
        or "REDUZIDO" in risk_text
    ):

        return "🟢"

    return "⚪"


# ==========================================================
# ÍCONE DE SINAL
# ==========================================================

def signal_icon(
    signal,
):
    """
    Retorna um ícone conforme o sinal.
    """

    if signal is None:

        return "⚪"

    signal_text = str(
        signal
    ).strip().upper()

    if (
        "POSITIVO" in signal_text
        or "COMPRA" in signal_text
        or "BUY" in signal_text
    ):

        return "🟢"

    if (
        "NEGATIVO" in signal_text
        or "VENDA" in signal_text
        or "SELL" in signal_text
    ):

        return "🔴"

    return "🟡"


# ==========================================================
# ÍCONE DE TENDÊNCIA
# ==========================================================

def trend_icon(
    trend,
):
    """
    Retorna um ícone conforme a tendência.
    """

    if trend is None:

        return "⚪"

    trend_text = str(
        trend
    ).strip().upper()

    if (
        "ALTA" in trend_text
        or "ALTA" == trend_text
        or "BULLISH" in trend_text
    ):

        return "📈"

    if (
        "BAIXA" in trend_text
        or "BEARISH" in trend_text
    ):

        return "📉"

    return "➡️"


# ==========================================================
# STATUS DOS DADOS
# ==========================================================

def data_status_icon(
    status,
):
    """
    Retorna ícone para o status dos dados.
    """

    if status is None:

        return "⚪"

    status_text = str(
        status
    ).strip().upper()

    if (
        "CONSISTENTE" in status_text
        or "VALIDO" in status_text
        or "VÁLIDO" in status_text
    ):

        return "🟢"

    if (
        "INCOMPLETO" in status_text
        or "PARCIAL" in status_text
    ):

        return "🟡"

    if (
        "INCONSISTENTE" in status_text
        or "INVALIDO" in status_text
        or "INVÁLIDO" in status_text
    ):

        return "🔴"

    return "⚪"


# ==========================================================
# LIMPEZA DE DADOS
# ==========================================================

def clean_numeric_data(
    data,
):
    """
    Cria uma cópia dos dados mantendo somente
    valores numéricos válidos nos campos numéricos.

    Não altera o dicionário original.
    """

    if not isinstance(
        data,
        dict,
    ):

        return {}

    cleaned = dict(
        data
    )

    numeric_fields = [
        "price",
        "ma21",
        "ma200",
        "rsi",
        "volatility",
    ]

    for field in numeric_fields:

        if field in cleaned:

            value = safe_float(
                cleaned[field]
            )

            cleaned[field] = value

    return cleaned


# ==========================================================
# RESUMO DE VALIDAÇÃO
# ==========================================================

def validation_summary(
    data,
):
    """
    Retorna uma mensagem curta para o Dashboard.
    """

    validation = validate_indicators(
        data
    )

    return (
        validation["status_icon"]
        + " "
        + validation["status"]
        + " — "
        + validation["message"]
    )
