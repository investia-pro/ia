"""
InvestIA PRO
Motor de Análise

Versão: v0.6
Fase: 2.3 - Score InvestIA unificado
"""

from score import (
    calculate_score_details,
)

from config import (
    RSI_OVERSOLD,
    RSI_OVERBOUGHT,
)


# ==========================================================
# ANÁLISE DE TENDÊNCIA
# ==========================================================

def analyze_trend(
    price,
    ma21,
    ma200,
):
    """
    Analisa a tendência de curto e longo prazo.
    """

    reasons = []

    short_term_positive = (
        price > ma21
    )

    long_term_positive = (
        price > ma200
    )

    # ======================================================
    # CURTO PRAZO
    # ======================================================

    if short_term_positive:

        reasons.append(
            "Preço acima da média móvel de 21 períodos."
        )

    else:

        reasons.append(
            "Preço abaixo da média móvel de 21 períodos."
        )

    # ======================================================
    # LONGO PRAZO
    # ======================================================

    if long_term_positive:

        reasons.append(
            "Preço acima da média móvel de 200 períodos."
        )

    else:

        reasons.append(
            "Preço abaixo da média móvel de 200 períodos."
        )

    # ======================================================
    # TENDÊNCIA FINAL
    # ======================================================

    if (
        short_term_positive
        and long_term_positive
    ):

        trend = "Positiva"

    elif (
        not short_term_positive
        and not long_term_positive
    ):

        trend = "Negativa"

    else:

        trend = "Neutra"

    return (
        trend,
        reasons,
    )


# ==========================================================
# ANÁLISE DO RSI
# ==========================================================

def analyze_rsi(
    rsi,
):
    """
    Interpreta o RSI.
    """

    if rsi <= RSI_OVERSOLD:

        return (
            "Sobrevenda",
            "RSI indica possível sobrevenda.",
        )

    if rsi >= RSI_OVERBOUGHT:

        return (
            "Sobrecompra",
            "RSI indica possível sobrecompra.",
        )

    return (
        "Neutro",
        "RSI em zona neutra.",
    )


# ==========================================================
# ANÁLISE DE RISCO
# ==========================================================

def analyze_risk(
    volatility,
):
    """
    Classifica o risco com base na volatilidade.
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
    Gera a recomendação final.

    O Score é a referência principal.
    Tendência e risco funcionam como filtros.
    """

    # ======================================================
    # SCORE FORTE
    # ======================================================

    if score >= 80:

        if trend == "Positiva":

            return "Compra"

        return "Aguardar"

    # ======================================================
    # SCORE BOM
    # ======================================================

    if score >= 65:

        if (
            trend == "Positiva"
            and risk != "Alto"
        ):

            return "Compra"

        return "Aguardar"

    # ======================================================
    # SCORE NEUTRO
    # ======================================================

    if score >= 50:

        return "Aguardar"

    # ======================================================
    # SCORE FRACO
    # ======================================================

    if score >= 35:

        if trend == "Negativa":

            return "Venda"

        return "Aguardar"

    # ======================================================
    # SCORE MUITO FRACO
    # ======================================================

    return "Venda"


# ==========================================================
# MOTOR PRINCIPAL
# ==========================================================

def analyze_asset(
    data,
):
    """
    Executa a análise completa do ativo.

    O Score é calculado exclusivamente
    pelo score.py.
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
    # SCORE CENTRAL
    # ======================================================

    score_result = calculate_score_details(
        data
    )

    score = score_result[
        "score"
    ]

    classification = score_result[
        "classification"
    ]

    signal = score_result[
        "signal"
    ]

    breakdown = score_result[
        "breakdown"
    ]

    # ======================================================
    # TENDÊNCIA
    # ======================================================

    trend, trend_reasons = analyze_trend(
        price,
        ma21,
        ma200,
    )

    # ======================================================
    # RSI
    # ======================================================

    rsi_status, rsi_reason = analyze_rsi(
        rsi
    )

    # ======================================================
    # RISCO
    # ======================================================

    risk = analyze_risk(
        volatility
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
    # JUSTIFICATIVAS
    # ======================================================

    reasons = []

    reasons.extend(
        trend_reasons
    )

    reasons.append(
        rsi_reason
    )

    # ======================================================
    # RISCO
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

        "score":
            score,

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

        "rsi_status":
            rsi_status,

        "breakdown":
            breakdown,

        "reasons":
            reasons,
    }
