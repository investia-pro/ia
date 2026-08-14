"""
InvestIA PRO
Motor de Score

Versão: v0.6
Fase: 2.7.6 - Correção do Breakdown do Score
"""

from config import (
    BUY_SCORE,
    SELL_SCORE,
    RSI_OVERSOLD,
    RSI_OVERBOUGHT,
)


# ==========================================================
# LIMITAÇÃO DO SCORE
# ==========================================================

def clamp_score(score):
    """
    Mantém o Score entre 0 e 100.
    """

    try:
        score = float(score)
    except (TypeError, ValueError):
        score = 0

    return max(
        0,
        min(
            100,
            int(round(score)),
        ),
    )


# ==========================================================
# VALIDAÇÃO DOS DADOS
# ==========================================================

def validate_score_data(data):
    """
    Valida os dados necessários para o cálculo do Score.
    """

    if data is None:
        raise ValueError(
            "Dados não fornecidos para o Score."
        )

    if not isinstance(data, dict):
        raise ValueError(
            "Os dados do Score devem estar em formato de dicionário."
        )

    required = [
        "price",
        "ma21",
        "ma200",
        "rsi",
    ]

    missing = [
        field
        for field in required
        if field not in data
        or data[field] is None
    ]

    if missing:
        raise ValueError(
            "Dados ausentes para o Score: "
            + ", ".join(missing)
        )


# ==========================================================
# CONTRIBUIÇÃO DOS INDICADORES
# ==========================================================

def get_score_breakdown(data):
    """
    Calcula detalhadamente a contribuição
    de cada indicador para o Score InvestIA.

    Score base:
        50 pontos

    MA21:
        +10 / -10

    MA200:
        +20 / -20

    RSI:
        +10 / -10 / 0

    Exemplo:

        Preço = 41.82
        MA21  = 41.67
        MA200 = 38.98
        RSI   = 45.42

        50 + 10 + 20 + 0 = 80
    """

    validate_score_data(data)

    # ======================================================
    # CONVERSÃO
    # ======================================================

    try:

        price = float(data["price"])
        ma21 = float(data["ma21"])
        ma200 = float(data["ma200"])
        rsi = float(data["rsi"])

    except (TypeError, ValueError) as error:

        raise ValueError(
            "Os valores dos indicadores precisam ser numéricos."
        ) from error

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
    # BREAKDOWN COMPLETO
    # ======================================================

    return {

        # --------------------------------------------------
        # BASE
        # --------------------------------------------------

        "base": base,

        # --------------------------------------------------
        # MA21
        # --------------------------------------------------

        "ma21": {

            "value": ma21,

            "points": ma21_points,

            "signal": ma21_signal,

            "reason": ma21_reason,

        },

        # --------------------------------------------------
        # MA200
        # --------------------------------------------------

        "ma200": {

            "value": ma200,

            "points": ma200_points,

            "signal": ma200_signal,

            "reason": ma200_reason,

        },

        # --------------------------------------------------
        # RSI
        # --------------------------------------------------

        "rsi": {

            "value": rsi,

            "points": rsi_points,

            "signal": rsi_signal,

            "reason": rsi_reason,

        },

        # --------------------------------------------------
        # VALORES UTILIZADOS
        # --------------------------------------------------

        "values": {

            "price": price,

            "ma21": ma21,

            "ma200": ma200,

            "rsi": rsi,

        },

        # --------------------------------------------------
        # CÁLCULO
        # --------------------------------------------------

        "raw_score": raw_score,

        "score": final_score,

    }


# ==========================================================
# SCORE PRINCIPAL
# ==========================================================

def calculate_investia_score(data):
    """
    Calcula somente o Score InvestIA.
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
    - Classificação
    - Sinal
    - Breakdown
    """

    breakdown = get_score_breakdown(
        data
    )

    score = breakdown["score"]

    return {

        "score": score,

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

    }


# ==========================================================
# RESUMO DO BREAKDOWN
# ==========================================================

def get_score_summary(data):
    """
    Retorna um resumo textual do cálculo
    para utilização no Dashboard Executivo.
    """

    breakdown = get_score_breakdown(
        data
    )

    return {

        "base":
            breakdown["base"],

        "ma21_points":
            breakdown["ma21"]["points"],

        "ma21_signal":
            breakdown["ma21"]["signal"],

        "ma200_points":
            breakdown["ma200"]["points"],

        "ma200_signal":
            breakdown["ma200"]["signal"],

        "rsi_points":
            breakdown["rsi"]["points"],

        "rsi_signal":
            breakdown["rsi"]["signal"],

        "raw_score":
            breakdown["raw_score"],

        "score":
            breakdown["score"],

    }
