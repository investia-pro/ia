# ==========================================
# InvestIA PRO
# Score Inteligente
# ==========================================

from config import PESOS


def calcular_score(indicadores):

    score = 0
    motivos = []

    # ----------------------------------
    # RSI
    # ----------------------------------

    rsi = indicadores["RSI"]

    if 45 <= rsi <= 65:
        score += PESOS["rsi"]
        motivos.append("RSI saudável")

    elif 30 <= rsi < 45:
        score += 15
        motivos.append("RSI em recuperação")

    elif rsi < 30:
        score += 10
        motivos.append("RSI sobrevendido")

    elif rsi > 70:
        motivos.append("RSI sobrecomprado")

    # ----------------------------------
    # Tendência
    # ----------------------------------

    tendencia = indicadores["TENDENCIA"]

    score += tendencia * (PESOS["tendencia"] / 3)

    if tendencia == 3:
        motivos.append("Tendência forte de alta")

    elif tendencia == 2:
        motivos.append("Tendência positiva")

    elif tendencia == 1:
        motivos.append("Tendência fraca")

    else:
        motivos.append("Sem tendência")

    # ----------------------------------
    # MACD
    # ----------------------------------

    if indicadores["MACD"] > indicadores["SINAL"]:

        score += PESOS["macd"]

        motivos.append("MACD positivo")

    # ----------------------------------
    # Médias móveis
    # ----------------------------------

    mm = 0

    if indicadores["MM9"] > indicadores["MM21"]:
        mm += 1

    if indicadores["MM21"] > indicadores["MM72"]:
        mm += 1

    if indicadores["MM72"] > indicadores["MM200"]:
        mm += 1

    score += mm * (PESOS["medias"] / 3)

    if mm == 3:
        motivos.append("Médias alinhadas")

    # ----------------------------------
    # Volume
    # ----------------------------------

    if indicadores["VOLUME_MEDIO"] > 0:

        score += PESOS["volume"]

        motivos.append("Volume consistente")

    # ----------------------------------
    # Limites
    # ----------------------------------

    score = round(max(0, min(100, score)))

    # ----------------------------------
    # Recomendação
    # ----------------------------------

    if score >= 85:
        recomendacao = "🟢 Compra Forte"

    elif score >= 70:
        recomendacao = "🟢 Compra"

    elif score >= 50:
        recomendacao = "🟡 Neutro"

    else:
        recomendacao = "🔴 Venda"

    return score, recomendacao, motivos
