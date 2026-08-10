"""
InvestIA PRO
Motor de Análise

Versão: v0.6
Fase: 1.2

Integração com Score InvestIA 2.0
"""

from score import calculate_investia_score


# ==========================================================
# ANÁLISE DO ATIVO
# ==========================================================

def analyze_asset(data):
    """
    Recebe os indicadores técnicos e gera uma avaliação
    utilizando o Score InvestIA 2.0.

    Mantém compatibilidade com o app.py da v0.5.3.
    """

    # ======================================================
    # VALIDAÇÃO
    # ======================================================

    if not isinstance(data, dict):

        raise TypeError(
            "Os dados do ativo devem ser fornecidos "
            "em formato de dicionário."
        )


    required_fields = [
        "price",
        "ma21",
        "ma200",
        "rsi",
        "volatility",
    ]


    missing_fields = [
        field
        for field in required_fields
        if field not in data
    ]


    if missing_fields:

        raise ValueError(
            "Indicadores ausentes: "
            + ", ".join(missing_fields)
        )


    # ======================================================
    # SCORE INVESTIA 2.0
    # ======================================================

    score_result = calculate_investia_score(
        data
    )


    score = score_result["score"]


    classification = score_result[
        "classification"
    ]


    signal = score_result[
        "signal"
    ]


    # ======================================================
    # TENDÊNCIA
    # ======================================================

    trend_score = score_result[
        "trend"
    ]


    if trend_score >= 75:

        trend = "Positiva"

    elif trend_score >= 60:

        trend = "Moderadamente Positiva"

    elif trend_score >= 40:

        trend = "Neutra"

    elif trend_score >= 25:

        trend = "Moderadamente Negativa"

    else:

        trend = "Negativa"


    # ======================================================
    # RECOMENDAÇÃO
    # ======================================================

    if score >= 75:

        recommendation = "Compra"

    elif score >= 60:

        recommendation = "Compra Moderada"

    elif score >= 40:

        recommendation = "Aguardar"

    elif score >= 25:

        recommendation = "Venda Moderada"

    else:

        recommendation = "Venda"


    # ======================================================
    # RISCO
    # ======================================================

    risk_score = score_result[
        "risk"
    ]


    if risk_score >= 75:

        risk = "Baixo"

    elif risk_score >= 50:

        risk = "Moderado"

    elif risk_score >= 30:

        risk = "Alto"

    else:

        risk = "Muito Alto"


    # ======================================================
    # FUNDAMENTAÇÃO
    # ======================================================

    reasons = score_result.get(
        "reasons",
        [],
    )


    # ======================================================
    # RESULTADO
    # ======================================================

    return {

        # ----------------------------------------------
        # Score principal
        # ----------------------------------------------

        "score": score,

        "classification": classification,

        "signal": signal,


        # ----------------------------------------------
        # Tendência
        # ----------------------------------------------

        "trend": trend,


        # ----------------------------------------------
        # Recomendação
        # ----------------------------------------------

        "recommendation": recommendation,


        # ----------------------------------------------
        # Risco
        # ----------------------------------------------

        "risk": risk,


        # ----------------------------------------------
        # Scores internos
        # ----------------------------------------------

        "technical": score_result[
            "technical"
        ],

        "rsi_score": score_result[
            "rsi"
        ],

        "ma21_score": score_result[
            "ma21"
        ],

        "ma200_score": score_result[
            "ma200"
        ],

        "trend_score": trend_score,

        "risk_score": risk_score,


        # ----------------------------------------------
        # Fundamentação
        # ----------------------------------------------

        "reasons": reasons,

    }
