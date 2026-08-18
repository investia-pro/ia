"""
InvestIA PRO
Motor de Score

Versão: v0.6
Fase: 2.9.3 - Confiabilidade do Score
"""

import math

from config import (
    BUY_SCORE,
    SELL_SCORE,
    RSI_OVERSOLD,
    RSI_OVERBOUGHT,
)


# ==========================================================
# CONFIGURAÇÃO DOS INDICADORES
# ==========================================================

REQUIRED_SCORE_FIELDS = [
    "price",
    "ma21",
    "ma200",
    "rsi",
]


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def _is_valid_number(value):
    """
    Verifica se o valor é numérico, finito e válido.
    """

    try:

        if value is None:
            return False

        value = float(value)

        return math.isfinite(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return False


def _safe_float(value):
    """
    Converte um valor para float com segurança.

    Retorna None quando o valor é inválido.
    """

    if not _is_valid_number(
        value
    ):

        return None

    return float(value)


# ==========================================================
# VALIDAÇÃO DOS DADOS DO SCORE
# ==========================================================

def validate_score_data(data):
    """
    Valida os dados necessários para calcular
    o Score InvestIA.

    Retorna um dicionário contendo:

        valid
        missing
        invalid
        available
        message
    """

    if data is None:

        return {

            "valid": False,

            "missing":
                REQUIRED_SCORE_FIELDS.copy(),

            "invalid": [],

            "available": [],

            "message":
                "Dados não fornecidos para o Score.",

        }

    if not isinstance(
        data,
        dict,
    ):

        return {

            "valid": False,

            "missing":
                REQUIRED_SCORE_FIELDS.copy(),

            "invalid": [],

            "available": [],

            "message":
                "Formato de dados inválido para o Score.",

        }

    missing = []
    invalid = []
    available = []

    for field in REQUIRED_SCORE_FIELDS:

        if field not in data:

            missing.append(
                field
            )

            continue

        value = data.get(
            field
        )

        if value is None:

            missing.append(
                field
            )

            continue

        if not _is_valid_number(
            value
        ):

            invalid.append(
                field
            )

            continue

        available.append(
            field
        )

    valid = (
        len(missing) == 0
        and len(invalid) == 0
    )

    if valid:

        message = (
            "Todos os indicadores necessários "
            "para o Score estão disponíveis."
        )

    elif missing:

        message = (
            "O Score não pode ser considerado "
            "confiável porque existem indicadores "
            "necessários ausentes: "
            + ", ".join(missing)
            + "."
        )

    else:

        message = (
            "O Score não pode ser considerado "
            "confiável porque existem indicadores "
            "com valores inválidos: "
            + ", ".join(invalid)
            + "."
        )

    return {

        "valid":
            valid,

        "missing":
            missing,

        "invalid":
            invalid,

        "available":
            available,

        "message":
            message,

    }


# ==========================================================
# LIMITAÇÃO DO SCORE
# ==========================================================

def clamp_score(score):
    """
    Mantém o Score entre 0 e 100.
    """

    try:

        score = float(
            score
        )

    except (
        TypeError,
        ValueError,
    ):

        return 0

    if not math.isfinite(
        score
    ):

        return 0

    return max(
        0,
        min(
            100,
            int(
                round(
                    score
                )
            ),
        ),
    )


# ==========================================================
# CONTRIBUIÇÃO DOS INDICADORES
# ==========================================================

def get_score_breakdown(data):
    """
    Calcula a contribuição individual
    de cada indicador para o Score.

    Score base:
        50 pontos

    MA21:
        +10 / -10

    MA200:
        +20 / -20

    RSI:
        +10 / -10 / 0

    O cálculo somente é executado quando
    todos os indicadores necessários são válidos.
    """

    validation = validate_score_data(
        data
    )

    if not validation["valid"]:

        raise ValueError(
            validation["message"]
        )

    price = _safe_float(
        data["price"]
    )

    ma21 = _safe_float(
        data["ma21"]
    )

    ma200 = _safe_float(
        data["ma200"]
    )

    rsi = _safe_float(
        data["rsi"]
    )

    # ======================================================
    # SEGURANÇA ADICIONAL
    # ======================================================

    if (
        price is None
        or ma21 is None
        or ma200 is None
        or rsi is None
    ):

        raise ValueError(
            "Não foi possível validar "
            "os valores dos indicadores."
        )

    # ======================================================
    # BASE
    # ======================================================

    base = 50

    # ======================================================
    # MA21
    # ======================================================

    if price > ma21:

        ma21_points = 10

        ma21_signal = "Positivo"

        ma21_reason = (
            "Preço acima da MA21."
        )

    elif price < ma21:

        ma21_points = -10

        ma21_signal = "Negativo"

        ma21_reason = (
            "Preço abaixo da MA21."
        )

    else:

        ma21_points = 0

        ma21_signal = "Neutro"

        ma21_reason = (
            "Preço alinhado à MA21."
        )

    # ======================================================
    # MA200
    # ======================================================

    if price > ma200:

        ma200_points = 20

        ma200_signal = "Positivo"

        ma200_reason = (
            "Preço acima da MA200."
        )

    elif price < ma200:

        ma200_points = -20

        ma200_signal = "Negativo"

        ma200_reason = (
            "Preço abaixo da MA200."
        )

    else:

        ma200_points = 0

        ma200_signal = "Neutro"

        ma200_reason = (
            "Preço alinhado à MA200."
        )

    # ======================================================
    # RSI
    # ======================================================

    if rsi <= RSI_OVERSOLD:

        rsi_points = 10

        rsi_signal = "Positivo"

        rsi_reason = (
            "RSI em região de sobrevenda."
        )

    elif rsi >= RSI_OVERBOUGHT:

        rsi_points = -10

        rsi_signal = "Negativo"

        rsi_reason = (
            "RSI em região de sobrecompra."
        )

    else:

        rsi_points = 0

        rsi_signal = "Neutro"

        rsi_reason = (
            "RSI em região neutra."
        )

    # ======================================================
    # SCORE BRUTO
    # ======================================================

    raw_score = (
        base
        + ma21_points
        + ma200_points
        + rsi_points
    )

    # ======================================================
    # SCORE FINAL
    # ======================================================

    final_score = clamp_score(
        raw_score
    )

    # ======================================================
    # RETORNO
    # ======================================================

    return {

        "base":
            base,

        "ma21": {

            "points":
                ma21_points,

            "signal":
                ma21_signal,

            "reason":
                ma21_reason,

        },

        "ma200": {

            "points":
                ma200_points,

            "signal":
                ma200_signal,

            "reason":
                ma200_reason,

        },

        "rsi": {

            "points":
                rsi_points,

            "signal":
                rsi_signal,

            "reason":
                rsi_reason,

        },

        "raw_score":
            raw_score,

        "score":
            final_score,

    }


# ==========================================================
# SCORE PRINCIPAL
# ==========================================================

def calculate_investia_score(data):
    """
    Calcula o Score InvestIA de 0 a 100.

    O cálculo somente ocorre quando todos
    os indicadores obrigatórios são válidos.
    """

    breakdown = get_score_breakdown(
        data
    )

    return breakdown["score"]


# ==========================================================
# CLASSIFICAÇÃO
# ==========================================================

def classify_score(score):
    """
    Classifica o Score InvestIA.
    """

    score = clamp_score(
        score
    )

    if score >= 80:

        return "FORTE"

    if score >= 65:

        return "BOM"

    if score >= 50:

        return "NEUTRO"

    if score >= 35:

        return "FRACO"

    return "MUITO FRACO"


# ==========================================================
# SINAL
# ==========================================================

def classify_signal(score):
    """
    Define o sinal do Score.
    """

    score = clamp_score(
        score
    )

    if score >= BUY_SCORE:

        return "POSITIVO"

    if score <= SELL_SCORE:

        return "NEGATIVO"

    return "NEUTRO"


# ==========================================================
# SCORE COMPLETO
# ==========================================================

def calculate_score_details(data):
    """
    Retorna o Score completo com:

        - Score
        - classificação
        - sinal
        - breakdown
        - confiabilidade
        - validação dos dados
    """

    validation = validate_score_data(
        data
    )

    # ======================================================
    # DADOS INVÁLIDOS
    # ======================================================

    if not validation["valid"]:

        return {

            "score":
                None,

            "classification":
                "INDEFINIDO",

            "signal":
                "INDEFINIDO",

            "breakdown":
                {},

            "score_reliable":
                False,

            "reliable":
                False,

            "validation":
                validation,

            "missing_indicators":
                validation["missing"],

            "invalid_indicators":
                validation["invalid"],

            "message":
                validation["message"],

        }

    # ======================================================
    # CÁLCULO
    # ======================================================

    breakdown = get_score_breakdown(
        data
    )

    score = breakdown["score"]

    # ======================================================
    # RETORNO
    # ======================================================

    return {

        "score":
            score,

        "classification":
            classify_score(
                score
            ),

        "signal":
            classify_signal(
                score
            ),

        "breakdown":
            breakdown,

        "score_reliable":
            True,

        "reliable":
            True,

        "validation":
            validation,

        "missing_indicators":
            [],

        "invalid_indicators":
            [],

        "message":
            "Score calculado com todos os "
            "indicadores necessários disponíveis.",

    }


# ==========================================================
# STATUS DE CONFIABILIDADE
# ==========================================================

def get_score_reliability(
    data,
):
    """
    Retorna somente o status de confiabilidade
    do Score.

    Útil para o Dashboard.
    """

    validation = validate_score_data(
        data
    )

    if validation["valid"]:

        return {

            "reliable":
                True,

            "status":
                "CONFIÁVEL",

            "icon":
                "🟢",

            "message":
                "Todos os indicadores "
                "necessários estão disponíveis.",

            "missing":
                [],

            "invalid":
                [],

        }

    return {

        "reliable":
            False,

        "status":
            "NÃO CONFIÁVEL",

        "icon":
            "🔴",

        "message":
            validation["message"],

        "missing":
            validation["missing"],

        "invalid":
            validation["invalid"],

    }
