"""
InvestIA PRO
Módulo de análise inteligente de ativos

Responsável por transformar indicadores
em uma avaliação de investimento.
"""


def analyze_asset(data):
    """
    Recebe dados do ativo e retorna uma análise.

    Esperado:

    data = {
        "price": preço atual,
        "rsi": RSI,
        "ma21": média móvel 21,
        "ma200": média móvel 200,
        "volatility": volatilidade
    }

    """

    score = 0
    reasons = []


    # =========================
    # Análise de tendência
    # =========================

    if data["price"] > data["ma21"]:
        score += 1
        reasons.append(
            "Preço acima da média móvel de curto prazo."
        )

    else:
        score -= 1
        reasons.append(
            "Preço abaixo da média móvel de curto prazo."
        )


    if data["price"] > data["ma200"]:
        score += 2
        reasons.append(
            "Ativo acima da média móvel de longo prazo."
        )

    else:
        score -= 2
        reasons.append(
            "Ativo abaixo da média móvel de longo prazo."
        )


    # =========================
    # Análise RSI
    # =========================

    rsi = data["rsi"]


    if rsi < 30:

        score += 2

        reasons.append(
            "RSI indica possível região de sobrevenda."
        )


    elif rsi > 70:

        score -= 2

        reasons.append(
            "RSI indica possível sobrecompra."
        )


    else:

        reasons.append(
            "RSI dentro da zona neutra."
        )



    # =========================
    # Classificação
    # =========================

    if score >= 3:

        recommendation = "Compra"

        trend = "Positiva"


    elif score <= -3:

        recommendation = "Venda"

        trend = "Negativa"


    else:

        recommendation = "Aguardar"

        trend = "Neutra"



    # =========================
    # Risco
    # =========================

    volatility = data.get(
        "volatility",
        0
    )


    if volatility > 0.03:

        risk = "Alto"

    elif volatility > 0.015:

        risk = "Moderado"

    else:

        risk = "Baixo"



    return {

        "score": score,

        "tendencia": trend,

        "recomendacao": recommendation,

        "risco": risk,

        "justificativas": reasons

    }
