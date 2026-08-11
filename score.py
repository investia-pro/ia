"""
InvestIA PRO
Motor de Score

Versão: v0.6
Fase: 2.4 - Explicabilidade do Score
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

    return max(
        0,
        min(
            100,
            int(round(score)),
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
    """

    if data is None:
        raise ValueError(
            "Dados não fornecidos para o detalhamento do Score."
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

    price = float(data["price"])
    ma21 = float(data["ma21"])
    ma200 = float(data["ma200"])
    rsi = float(data["rsi"])

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

        "base": base,

        "ma21": {
            "points": ma21_points,
            "signal": ma21_signal,
            "reason": ma21_reason,
        },

        "ma200": {
            "points": ma200_points,
            "signal": ma200_signal,
            "reason": ma200_reason,
        },

        "rsi": {
            "points": rsi_points,
            "signal": rsi_signal,
            "reason": rsi_reason,
        },

        "raw_score": raw_score,

        "score": final_score,
    }


# ==========================================================
# SCORE PRINCIPAL
# ==========================================================

def calculate_investia_score(data):
    """
    Calcula o Score InvestIA de 0 a 100.
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
    Retorna o Score completo com
    classificação, sinal e breakdown.
    """

    breakdown = get_score_breakdown(
        data
    )

    score = breakdown["score"]

    return {

        "score": score,

        "classification":
            classify_score(score),

        "signal":
            classify_signal(score),

        "breakdown":
            breakdown,
    }
