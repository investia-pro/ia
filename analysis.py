"""
InvestIA PRO
Motor de Análise

Versão: v0.5.3 Stable
"""

from config import (
    BUY_SCORE,
    SELL_SCORE,
    RSI_OVERSOLD,
    RSI_OVERBOUGHT,
)


def analyze_asset(data):
    """
    Recebe os indicadores técnicos e gera
    uma avaliação do ativo.
    """

    score = 0
    reasons = []

    price = data["price"]
    ma21 = data["ma21"]
    ma200 = data["ma200"]
    rsi = data["rsi"]
    volatility = data["volatility"]

    # =====================================
    # Tendência de curto prazo
    # =====================================

    if price > ma21:
        score += 1
        reasons.append("Preço acima da média móvel de 21 períodos.")
    else:
        score -= 1
        reasons.append("Preço abaixo da média móvel de 21 períodos.")

    # =====================================
    # Tendência de longo prazo
    # =====================================

    if price > ma200:
        score += 2
        reasons.append("Preço acima da média móvel de 200 períodos.")
    else:
        score -= 2
        reasons.append("Preço abaixo da média móvel de 200 períodos.")

    # =====================================
    # RSI
    # =====================================

    if rsi <= RSI_OVERSOLD:
        score += 2
        reasons.append("RSI indica possível sobrevenda.")

    elif rsi >= RSI_OVERBOUGHT:
        score -= 2
        reasons.append("RSI indica possível sobrecompra.")

    else:
        reasons.append("RSI em zona neutra.")

    # =====================================
    # Classificação
    # =====================================

    if score >= BUY_SCORE:
        recommendation = "Compra"
        trend = "Positiva"

    elif score <= SELL_SCORE:
        recommendation = "Venda"
        trend = "Negativa"

    else:
        recommendation = "Aguardar"
        trend = "Neutra"

    # =====================================
    # Risco
    # =====================================

    if volatility < 0.015:
        risk = "Baixo"

    elif volatility < 0.030:
        risk = "Moderado"

    else:
        risk = "Alto"

    return {

        "score": score,

        "trend": trend,

        "recommendation": recommendation,

        "risk": risk,

        "reasons": reasons

    }
