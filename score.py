"""
InvestIA PRO
Motor de Score

Versão: v0.6
Fase: 2.3 - Score InvestIA unificado
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
# SCORE BASE
# ==========================================================

def calculate_investia_score(data):
    """
    Calcula o Score InvestIA de 0 a 100.

    Componentes:

    Tendência de curto prazo  → MA21
    Tendência de longo prazo  → MA200
    RSI                      → momentum
    """

    if data is None:

        raise ValueError(
            "Dados não fornecidos para cálculo do Score."
        )

    required = [
        "price",
        "ma21",
        "ma200",
        "rsi",
        "volatility",
    ]

    missing = [
        field
        for field in required
        if field not in data
        or data[field] is None
    ]

    if missing:

        raise ValueError(
            "Dados ausentes para cálculo do Score: "
            + ", ".join(missing)
        )

    price = float(
        data["price"]
    )

    ma21 = float(
        data["ma21"]
    )

    ma200 = float(
        data["ma200"]
    )

    rsi = float(
        data["rsi"]
    )

    # ======================================================
    # SCORE INICIAL
    # ======================================================

    score = 50

    # ======================================================
    # MA21
    # ======================================================

    if price > ma21:

        score += 10

    elif price < ma21:

        score -= 10

    # ======================================================
    # MA200
    # ======================================================

    if price > ma200:

        score += 20

    elif price < ma200:

        score -= 20

    # ======================================================
    # RSI
    # ======================================================

    if rsi <= RSI_OVERSOLD:

        score += 10

    elif rsi >= RSI_OVERBOUGHT:

        score -= 10

    # ======================================================
    # SCORE FINAL
    # ======================================================

    return clamp_score(
        score
    )


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
    Classifica o sinal com base
    nos parâmetros definidos no config.py.
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
# CONTRIBUIÇÃO DOS INDICADORES
# ==========================================================

def get_score_breakdown(data):
    """
    Retorna a contribuição de cada componente
    para o Score InvestIA.

    Útil para a explicabilidade do sistema.
    """

    price = float(
        data["price"]
    )

    ma21 = float(
        data["ma21"]
    )

    ma200 = float(
        data["ma200"]
    )

    rsi = float(
        data["rsi"]
    )

    ma21_points = 0

    ma200_points = 0

    rsi_points = 0

    # ------------------------------------------------------
    # MA21
    # ------------------------------------------------------

    if price > ma21:

        ma21_points = 10

    elif price < ma21:

        ma21_points = -10

    # ------------------------------------------------------
    # MA200
    # ------------------------------------------------------

    if price > ma200:

        ma200_points = 20

    elif price < ma200:

        ma200_points = -20

    # ------------------------------------------------------
    # RSI
    # ------------------------------------------------------

    if rsi <= RSI_OVERSOLD:

        rsi_points = 10

    elif rsi >= RSI_OVERBOUGHT:

        rsi_points = -10

    return {

        "base": 50,

        "ma21": ma21_points,

        "ma200": ma200_points,

        "rsi": rsi_points,
    }


# ==========================================================
# SCORE COMPLETO
# ==========================================================

def calculate_score_details(data):
    """
    Retorna Score + classificação + sinal
    + detalhamento dos componentes.
    """

    score = calculate_investia_score(
        data
    )

    breakdown = get_score_breakdown(
        data
    )

    return {

        "score": score,

        "classification":
            classify_score(score),

        "signal":
            classify_signal(score),

        "breakdown":
            breakdown,
    }
