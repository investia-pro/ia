"""
InvestIA PRO
Motor de Análise

Versão: v0.6
Fase: 2.2 - Motor de decisão
"""

from config import (
    BUY_SCORE,
    SELL_SCORE,
    RSI_OVERSOLD,
    RSI_OVERBOUGHT,
)


# ==========================================================
# CLASSIFICAÇÃO DO SCORE
# ==========================================================

def classify_score(score):
    """
    Classifica o Score InvestIA.
    """

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
    Define o sinal principal da análise.
    """

    if score >= BUY_SCORE:
        return "POSITIVO"

    if score <= SELL_SCORE:
        return "NEGATIVO"

    return "NEUTRO"


# ==========================================================
# ANÁLISE DE TENDÊNCIA
# ==========================================================

def analyze_trend(
    price,
    ma21,
    ma200,
):
    """
    Avalia tendência de curto e longo prazo.
    """

    reasons = []

    short_term = price > ma21
    long_term = price > ma200

    # ------------------------------------------------------
    # Curto prazo
    # ------------------------------------------------------

    if short_term:

        reasons.append(
            "Preço acima da média móvel de 21 períodos."
        )

    else:

        reasons.append(
            "Preço abaixo da média móvel de 21 períodos."
        )

    # ------------------------------------------------------
    # Longo prazo
    # ------------------------------------------------------

    if long_term:

        reasons.append(
            "Preço acima da média móvel de 200 períodos."
        )

    else:

        reasons.append(
            "Preço abaixo da média móvel de 200 períodos."
        )

    # ------------------------------------------------------
    # Classificação
    # ------------------------------------------------------

    if short_term and long_term:

        trend = "Positiva"

    elif not short_term and not long_term:

        trend = "Negativa"

    else:

        trend = "Neutra"

    return trend, reasons


# ==========================================================
# ANÁLISE DO RSI
# ==========================================================

def analyze_rsi(rsi):
    """
    Interpreta o RSI.
    """

    reasons = []

    if rsi <= RSI_OVERSOLD:

        reasons.append(
            "RSI indica possível sobrevenda."
        )

        return 2, reasons

    if rsi >= RSI_OVERBOUGHT:

        reasons.append(
            "RSI indica possível sobrecompra."
        )

        return -2, reasons

    reasons.append(
        "RSI em zona neutra."
    )

    return 0, reasons


# ==========================================================
# ANÁLISE DE RISCO
# ==========================================================

def analyze_risk(volatility):
    """
    Classifica o risco pela volatilidade.
    """

    if volatility < 0.015:

        return "Baixo"

    if volatility < 0.030:

        return "Moderado"

    return "Alto"


# ==========================================================
# RECOMENDAÇÃO
# ==========================================================

def generate_recommendation(
    score,
    trend,
    risk,
):
    """
    Gera recomendação combinando score,
    tendência e risco.
    """

    # ------------------------------------------------------
    # Score muito forte
    # ------------------------------------------------------

    if score >= 80:

        if trend == "Positiva":

            return "Compra"

        if risk == "Alto":

            return "Aguardar"

        return "Compra"


    # ------------------------------------------------------
    # Score bom
    # ------------------------------------------------------

    if score >= 65:

        if trend == "Negativa":

            return "Aguardar"

        if risk == "Alto":

            return "Aguardar"

        return "Compra"


    # ------------------------------------------------------
    # Score neutro
    # ------------------------------------------------------

    if score >= 50:

        return "Aguardar"


    # ------------------------------------------------------
    # Score fraco
    # ------------------------------------------------------

    if score >= 35:

        if trend == "Positiva":

            return "Aguardar"

        return "Venda"


    # ------------------------------------------------------
    # Score muito fraco
    # ------------------------------------------------------

    return "Venda"


# ==========================================================
# MOTOR PRINCIPAL
# ==========================================================

def analyze_asset(data):
    """
    Recebe os indicadores técnicos e gera
    uma análise completa do ativo.

    Campos esperados:

    price
    ma21
    ma200
    rsi
    volatility
    """

    # ======================================================
    # VALIDAÇÃO
    # ======================================================

    if data is None:

        raise ValueError(
            "Dados de análise não fornecidos."
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
            "Dados ausentes para análise: "
            + ", ".join(missing)
        )

    # ======================================================
    # DADOS
    # ======================================================

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

    volatility = float(
        data["volatility"]
    )

    # ======================================================
    # SCORE
    # ======================================================

    score = 50

    reasons = []

    # ======================================================
    # TENDÊNCIA
    # ======================================================

    trend, trend_reasons = analyze_trend(
        price,
        ma21,
        ma200,
    )

    reasons.extend(
        trend_reasons
    )

    # ------------------------------------------------------
    # Curto prazo
    # ------------------------------------------------------

    if price > ma21:

        score += 10

    else:

        score -= 10

    # ------------------------------------------------------
    # Longo prazo
    # ------------------------------------------------------

    if price > ma200:

        score += 20

    else:

        score -= 20

    # ======================================================
    # RSI
    # ======================================================

    rsi_score, rsi_reasons = analyze_rsi(
        rsi
    )

    score += (
        rsi_score * 5
    )

    reasons.extend(
        rsi_reasons
    )

    # ======================================================
    # LIMITAÇÃO DO SCORE
    # ======================================================

    score = max(
        0,
        min(
            100,
            score,
        ),
    )

    # ======================================================
    # RISCO
    # ======================================================

    risk = analyze_risk(
        volatility
    )

    # ======================================================
    # CLASSIFICAÇÃO
    # ======================================================

    classification = classify_score(
        score
    )

    # ======================================================
    # SINAL
    # ======================================================

    signal = classify_signal(
        score
    )

    # ======================================================
    # RECOMENDAÇÃO
    # ======================================================

    recommendation = generate_recommendation(
        score,
        trend,
        risk,
    )

    # ======================================================
    # JUSTIFICATIVAS DE RISCO
    # ======================================================

    if risk == "Baixo":

        reasons.append(
            "Volatilidade baixa, indicando menor risco técnico."
        )

    elif risk == "Moderado":

        reasons.append(
            "Volatilidade moderada, exigindo atenção ao risco."
        )

    else:

        reasons.append(
            "Volatilidade elevada, indicando maior risco técnico."
        )

    # ======================================================
    # RETORNO
    # ======================================================

    return {

        "score": score,

        "classification":
            classification,

        "signal":
            signal,

        "trend":
            trend,

        "recommendation":
            recommendation,

        "risk":
            risk,

        "reasons":
            reasons,
    }
