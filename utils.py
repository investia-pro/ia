"""
InvestIA PRO
Utilitários e Funções Auxiliares

Versão: v0.6
Fase: 2.9.7 - Utilitários Robustos
"""

import math


# ==========================================================
# CONVERSÃO SEGURA
# ==========================================================

def safe_float(
    value,
    default=None,
):
    """
    Converte um valor para float com segurança.

    Retorna default caso o valor seja inválido,
    None ou não possa ser convertido.
    """

    try:

        if value is None:
            return default

        if isinstance(
            value,
            bool,
        ):
            return default

        converted = float(
            value
        )

        if math.isnan(
            converted
        ):

            return default

        if math.isinf(
            converted
        ):

            return default

        return converted

    except (
        TypeError,
        ValueError,
    ):

        return default


def safe_int(
    value,
    default=None,
):
    """
    Converte um valor para inteiro com segurança.
    """

    value = safe_float(
        value,
        default=None,
    )

    if value is None:
        return default

    try:

        return int(
            round(value)
        )

    except (
        TypeError,
        ValueError,
    ):

        return default


# ==========================================================
# VALIDAÇÃO DE VALORES
# ==========================================================

def is_valid_number(
    value,
):
    """
    Verifica se um valor é numérico,
    finito e válido.
    """

    return (
        safe_float(
            value,
            default=None,
        )
        is not None
    )


def is_valid_positive_number(
    value,
):
    """
    Verifica se um valor é numérico,
    válido e maior que zero.
    """

    value = safe_float(
        value,
        default=None,
    )

    if value is None:
        return False

    return value > 0


# ==========================================================
# VALIDAÇÃO DOS DADOS DA ANÁLISE
# ==========================================================

def validate_analysis_data(
    data,
):
    """
    Valida os dados necessários para
    executar a análise técnica.

    Campos obrigatórios:
        - price
        - ma21
        - ma200
        - rsi

    Campo opcional:
        - volatility
    """

    if data is None:
        return False

    if not isinstance(
        data,
        dict,
    ):
        return False

    required = [
        "price",
        "ma21",
        "ma200",
        "rsi",
    ]

    for field in required:

        if field not in data:
            return False

        value = safe_float(
            data.get(field),
            default=None,
        )

        if value is None:
            return False

    return True


def get_missing_analysis_fields(
    data,
):
    """
    Retorna uma lista com os campos
    obrigatórios ausentes ou inválidos.
    """

    required = [
        "price",
        "ma21",
        "ma200",
        "rsi",
    ]

    missing = []

    if not isinstance(
        data,
        dict,
    ):
        return required

    for field in required:

        value = safe_float(
            data.get(field),
            default=None,
        )

        if value is None:

            missing.append(
                field
            )

    return missing


# ==========================================================
# VALIDAÇÃO DE HISTÓRICO
# ==========================================================

def validate_history(
    history,
):
    """
    Valida um histórico de preços.

    A função não importa pandas diretamente,
    permitindo que utils.py permaneça leve.
    """

    if history is None:
        return False

    try:

        if history.empty:
            return False

        if len(history) == 0:
            return False

        return True

    except Exception:

        return False


def has_required_columns(
    data,
    columns,
):
    """
    Verifica se um DataFrame possui
    todas as colunas necessárias.
    """

    if data is None:
        return False

    if not columns:
        return True

    try:

        available_columns = list(
            data.columns
        )

        for column in columns:

            if column not in available_columns:
                return False

        return True

    except Exception:

        return False


# ==========================================================
# FORMATAÇÃO MONETÁRIA
# ==========================================================

def format_currency(
    value,
    symbol="R$",
):
    """
    Formata valores monetários no padrão brasileiro.

    Exemplos:

        40.5
        -> R$ 40,50

        1250.75
        -> R$ 1.250,75

        -50
        -> -R$ 50,00
    """

    value = safe_float(
        value,
        default=None,
    )

    if value is None:
        return "N/D"

    sign = ""

    if value < 0:

        sign = "-"
        value = abs(
            value
        )

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

    return (
        f"{sign}{symbol} "
        f"{formatted}"
    )


# ==========================================================
# FORMATAÇÃO DE PERCENTUAL
# ==========================================================

def format_percent(
    value,
    decimals=2,
    multiply=True,
):
    """
    Formata um valor percentual.

    Por padrão:

        0.015
        -> 1,50%

    Para valores já em percentual:

        format_percent(
            1.5,
            multiply=False,
        )

        -> 1,50%
    """

    value = safe_float(
        value,
        default=None,
    )

    if value is None:
        return "N/D"

    if multiply:

        value = value * 100

    decimals = safe_int(
        decimals,
        default=2,
    )

    if decimals is None:
        decimals = 2

    decimals = max(
        0,
        min(
            decimals,
            6,
        ),
    )

    formatted = (
        f"{value:,.{decimals}f}"
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

    return (
        f"{formatted}%"
    )


# ==========================================================
# FORMATAÇÃO NUMÉRICA
# ==========================================================

def format_number(
    value,
    decimals=2,
):
    """
    Formata números no padrão brasileiro.
    """

    value = safe_float(
        value,
        default=None,
    )

    if value is None:
        return "N/D"

    decimals = safe_int(
        decimals,
        default=2,
    )

    if decimals is None:
        decimals = 2

    decimals = max(
        0,
        min(
            decimals,
            6,
        ),
    )

    return (
        f"{value:,.{decimals}f}"
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


# ==========================================================
# FORMATAÇÃO DO SCORE
# ==========================================================

def format_score(
    score,
):
    """
    Formata o Score InvestIA.

    Mantém o resultado entre 0 e 100.
    """

    score = safe_float(
        score,
        default=None,
    )

    if score is None:
        return "N/D"

    score = max(
        0,
        min(
            100,
            int(
                round(score)
            ),
        ),
    )

    return f"{score}/100"


# ==========================================================
# ÍCONES DE RISCO
# ==========================================================

def risk_icon(
    risk,
):
    """
    Retorna um ícone para o nível de risco.
    """

    if risk is None:
        return "⚪"

    risk = str(
        risk
    ).strip().lower()

    risk_map = {

        "baixo":
            "🟢",

        "moderado":
            "🟡",

        "alto":
            "🔴",

        "muito alto":
            "🔴",

        "indisponível":
            "⚪",

        "indisponivel":
            "⚪",
    }

    return risk_map.get(
        risk,
        "⚪",
    )


# ==========================================================
# ÍCONES DE SINAL
# ==========================================================

def signal_icon(
    signal,
):
    """
    Retorna um ícone visual para o sinal.
    """

    if signal is None:
        return "⚪"

    signal = str(
        signal
    ).strip().upper()

    signal_map = {

        "POSITIVO":
            "🟢",

        "COMPRA":
            "🟢",

        "NEGATIVO":
            "🔴",

        "VENDA":
            "🔴",

        "NEUTRO":
            "🟡",

        "AGUARDAR":
            "🟡",
    }

    return signal_map.get(
        signal,
        "⚪",
    )


# ==========================================================
# ÍCONES DE TENDÊNCIA
# ==========================================================

def trend_icon(
    trend,
):
    """
    Retorna um ícone para a tendência.
    """

    if trend is None:
        return "➡️"

    trend = str(
        trend
    ).strip().lower()

    if trend in [
        "alta forte",
        "alta",
        "recuperação",
        "recuperacao",
    ]:

        return "📈"

    if trend in [
        "baixa forte",
        "baixa",
        "correção",
        "correcao",
    ]:

        return "📉"

    return "➡️"


# ==========================================================
# ÍCONES DE CLASSIFICAÇÃO
# ==========================================================

def classification_icon(
    classification,
):
    """
    Retorna um ícone para a classificação
    do Score InvestIA.
    """

    if classification is None:
        return "⚪"

    classification = str(
        classification
    ).strip().upper()

    classification_map = {

        "FORTE":
            "🟢",

        "BOM":
            "🟢",

        "NEUTRO":
            "🟡",

        "FRACO":
            "🟠",

        "MUITO FRACO":
            "🔴",
    }

    return classification_map.get(
        classification,
        "⚪",
    )


# ==========================================================
# NORMALIZAÇÃO DE ATIVO
# ==========================================================

def normalize_asset(
    asset,
):
    """
    Normaliza o código informado pelo usuário.

    Exemplos:

        petr4
        PETR4

        PETR4.SA
        PETR4.SA
    """

    if asset is None:
        return ""

    try:

        asset = (
            str(asset)
            .strip()
            .upper()
            .replace(
                " ",
                "",
            )
        )

        return asset

    except Exception:

        return ""


# ==========================================================
# NORMALIZAÇÃO DE RESULTADOS
# ==========================================================

def normalize_result_dict(
    result,
):
    """
    Garante que o resultado de uma análise
    seja um dicionário válido.
    """

    if result is None:
        return {}

    if not isinstance(
        result,
        dict,
    ):
        return {}

    return result


def get_result_value(
    result,
    *keys,
    default=None,
):
    """
    Obtém um valor de um resultado utilizando
    múltiplas chaves alternativas.

    Exemplo:

        get_result_value(
            result,
            "trend",
            "tendencia",
            default="Neutra"
        )
    """

    result = normalize_result_dict(
        result
    )

    for key in keys:

        if key in result:

            value = result.get(
                key
            )

            if value is not None:
                return value

    return default


# ==========================================================
# LIMITAÇÃO DE VALORES
# ==========================================================

def clamp(
    value,
    minimum,
    maximum,
):
    """
    Limita um valor entre mínimo e máximo.
    """

    value = safe_float(
        value,
        default=None,
    )

    minimum = safe_float(
        minimum,
        default=None,
    )

    maximum = safe_float(
        maximum,
        default=None,
    )

    if (
        value is None
        or minimum is None
        or maximum is None
    ):

        return None

    if minimum > maximum:

        minimum, maximum = (
            maximum,
            minimum,
        )

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


def clamp_score(
    score,
):
    """
    Mantém o Score InvestIA entre 0 e 100.
    """

    score = safe_float(
        score,
        default=0,
    )

    score = clamp(
        score,
        0,
        100,
    )

    return int(
        round(score)
    )


# ==========================================================
# FORMATAÇÃO DE DATA
# ==========================================================

def format_date(
    value,
):
    """
    Formata uma data para o padrão DD/MM/AAAA.

    Caso não seja possível converter,
    retorna o valor como texto.
    """

    if value is None:
        return "N/D"

    try:

        if hasattr(
            value,
            "strftime",
        ):

            return value.strftime(
                "%d/%m/%Y"
            )

        return str(
            value
        )

    except Exception:

        return "N/D"


# ==========================================================
# RESUMO DE PERFORMANCE
# ==========================================================

def calculate_return(
    initial_value,
    final_value,
):
    """
    Calcula o retorno percentual entre
    dois valores.

    Retorna um valor decimal.

    Exemplo:

        100 -> 110
        retorna 0.10
    """

    initial_value = safe_float(
        initial_value,
        default=None,
    )

    final_value = safe_float(
        final_value,
        default=None,
    )

    if (
        initial_value is None
        or final_value is None
    ):

        return None

    if initial_value == 0:
        return None

    return (
        final_value
        / initial_value
        - 1
    )


# ==========================================================
# COMPATIBILIDADE
# ==========================================================

def format_value(
    value,
    decimals=2,
):
    """
    Alias para format_number.

    Mantido para compatibilidade com
    versões anteriores do InvestIA PRO.
    """

    return format_number(
        value,
        decimals,
    )
