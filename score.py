"""
===========================================
InvestIA PRO
score.py
Algoritmo de Score
===========================================
"""

from config import (
    SCORE_COMPRA_FORTE,
    SCORE_COMPRA,
    SCORE_NEUTRO
)


def calcular_score(indicadores):

    score = 50

    motivos = []

    # ==========================
    # RSI
    # ==========================

    rsi = indicadores["RSI"]

    if 45 <= rsi <= 65:
        score += 10
        motivos.append("RSI em região saudável")

    elif rsi < 30:
        score += 15
        motivos.append("RSI indica sobrevenda")

    elif rsi > 70:
        score -= 15
        motivos.append("RSI indica sobrecompra")

    # ==========================
    # Médias
    # ==========================

    if indicadores["MM9"] > indicadores["MM21"]:
        score += 10
        motivos.append("MM9 acima da MM21")

    if indicadores["MM21"] > indicadores["MM72"]:
        score += 10
        motivos.append("MM21 acima da MM72")

    if indicadores["MM72"] > indicadores["MM200"]:
        score += 10
        motivos.append("MM72 acima da MM200")

    # ==========================
    # MACD
    # ==========================

    if indicadores["MACD"] > indicadores["MACD_SINAL"]:
        score += 15
        motivos.append("MACD acima da linha de sinal")

    else:
        score -= 10
        motivos.append("MACD abaixo da linha de sinal")

    # ==========================
    # Bollinger
    # ==========================

    preco = indicadores["Preço"]

    if preco < indicadores["BB_INF"]:
        score += 10
        motivos.append("Preço abaixo da Banda Inferior")

    elif preco > indicadores["BB_SUP"]:
        score -= 10
        motivos.append("Preço acima da Banda Superior")

    # ==========================
    # Limites
    # ==========================

    score = max(0, min(100, score))

    # ==========================
    # Recomendação
    # ==========================

    if score >= SCORE_COMPRA_FORTE:

        recomendacao = "🟢 Compra Forte"

    elif score >= SCORE_COMPRA:

        recomendacao = "🟢 Compra"

    elif score >= SCORE_NEUTRO:

        recomendacao = "🟡 Neutro"

    else:

        recomendacao = "🔴 Venda"

    return score, recomendacao, motivos
