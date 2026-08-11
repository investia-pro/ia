"""
InvestIA PRO
Motor de Análise

Versão: v0.6
Fase: 2.5 - Qualificação do Sinal e Resumo Executivo
"""

from score import calculate_score_details

from config import (
    RSI_OVERSOLD,
    RSI_OVERBOUGHT,
)


# ==========================================================
# TENDÊNCIA
# ==========================================================

def analyze_trend(price, ma21, ma200):
    """
    Analisa a tendência de curto e longo prazo.
    """

    reasons = []

    short_term_positive = price > ma21
    long_term_positive = price > ma200

    # ------------------------------------------------------
    # Curto prazo
    # ------------------------------------------------------

    if short_term_positive:

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

    if long_term_positive:

        reasons.append(
            "Preço acima da média móvel de 200 períodos."
        )

    else:

        reasons.append(
            "Preço abaixo da média móvel de 200 períodos."
        )

    # ------------------------------------------------------
    # Tendência final
    # ------------------------------------------------------

    if short_term_positive and long_term_positive:

        trend = "Positiva"

    elif not short_term_positive and not long_term_positive:

        trend = "Negativa"

    else:

        trend = "Neutra"

    return trend, reasons


# ==========================================================
# RSI
# ==========================================================

def analyze_rsi(rsi):
    """
    Interpreta o RSI.
    """

    if rsi <= RSI_OVERSOLD:

        return (
            "Sobrevenda",
            "RSI em região de sobrevenda."
        )

    if rsi >= RSI_OVERBOUGHT:

        return (
            "Sobrecompra",
            "RSI em região de sobrecompra."
        )

    return (
        "Neutro",
        "RSI em região neutra."
    )


# ==========================================================
# RISCO
# ==========================================================

def analyze_risk(volatility):
    """
    Classifica o risco através da volatilidade.
    """

    if volatility < 0.015:

        return "Baixo"

    if volatility < 0.030:

        return "Moderado"

    return "Alto"


# ==========================================================
# QUALIFICAÇÃO DO SINAL
# ==========================================================

def qualify_signal(
    score,
    trend,
    risk,
):
    """
    Qualifica a força do sinal considerando:

    - Score
    - Tendência
    - Risco
    """

    # ======================================================
    # SINAL MUITO FORTE
    # ======================================================

    if score >= 80:

        if trend == "Positiva" and risk == "Baixo":

            return {
                "level": "Compra Forte",
                "signal": "MUITO POSITIVO",
                "icon": "🟢",
            }

        if trend == "Positiva":

            return {
                "level": "Compra",
                "signal": "POSITIVO",
                "icon": "🟢",
            }

        return {
            "level": "Aguardar",
            "signal": "POSITIVO COM RESSALVAS",
            "icon": "🟡",
        }

    # ======================================================
    # SINAL BOM
    # ======================================================

    if score >= 65:

        if trend == "Positiva" and risk != "Alto":

            return {
                "level": "Compra",
                "signal": "POSITIVO",
                "icon": "🟢",
            }

        return {
            "level": "Aguardar",
            "signal": "LEVE POSITIVO",
            "icon": "🟡",
        }

    # ======================================================
    # SINAL NEUTRO
    # ======================================================

    if score >= 50:

        return {
            "level": "Aguardar",
            "signal": "NEUTRO",
            "icon": "🟡",
        }

    # ======================================================
    # SINAL FRACO
    # ======================================================

    if score >= 35:

        if trend == "Negativa":

            return {
                "level": "Venda",
                "signal": "NEGATIVO",
                "icon": "🟠",
            }

        return {
            "level": "Aguardar",
            "signal": "LEVE NEGATIVO",
            "icon": "🟡",
        }

    # ======================================================
    # SINAL MUITO FRACO
    # ======================================================

    return {
        "level": "Venda Forte",
        "signal": "MUITO NEGATIVO",
        "icon": "🔴",
    }


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
    """

    qualification = qualify_signal(
        score,
        trend,
        risk,
    )

    level = qualification["level"]

    if level == "Compra Forte":

        return "Compra"

    if level == "Compra":

        return "Compra"

    if level == "Venda Forte":

        return "Venda"

    if level == "Venda":

        return "Venda"

    return "Aguardar"


# ==========================================================
# RESUMO EXECUTIVO
# ==========================================================

def generate_executive_summary(
    asset,
    score,
    classification,
    trend,
    risk,
    recommendation,
    rsi_status,
):
    """
    Gera um resumo executivo da análise.
    """

    # ------------------------------------------------------
    # Tendência
    # ------------------------------------------------------

    if trend == "Positiva":

        trend_text = (
            "apresenta tendência positiva"
        )

    elif trend == "Negativa":

        trend_text = (
            "apresenta tendência negativa"
        )

    else:

        trend_text = (
            "apresenta tendência neutra"
        )

    # ------------------------------------------------------
    # Risco
    # ------------------------------------------------------

    if risk == "Baixo":

        risk_text = (
            "com baixo nível de volatilidade"
        )

    elif risk == "Moderado":

        risk_text = (
            "com volatilidade moderada"
        )

    else:

        risk_text = (
            "com elevada volatilidade"
        )

    # ------------------------------------------------------
    # RSI
    # ------------------------------------------------------

    if rsi_status == "Sobrevenda":

        rsi_text = (
            "O RSI está em região de sobrevenda."
        )

    elif rsi_status == "Sobrecompra":

        rsi_text = (
            "O RSI está em região de sobrecompra."
        )

    else:

        rsi_text = (
            "O RSI permanece em região neutra."
        )

    # ------------------------------------------------------
    # Resumo
    # ------------------------------------------------------

    summary = (
        f"{asset} {trend_text}, "
        f"com Score InvestIA de {score}/100, "
        f"classificação {classification} e "
        f"{risk_text}. "
        f"{rsi_text} "
        f"A recomendação técnica atual é "
        f"{recommendation}."
    )

    return summary


# ==========================================================
# MOTOR PRINCIPAL
# ==========================================================

def analyze_asset(data):
    """
    Executa a análise completa do ativo.

    O Score continua sendo calculado
    exclusivamente pelo score.py.
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

    price = float(data["price"])
    ma21 = float(data["ma21"])
    ma200 = float(data["ma200"])
    rsi = float(data["rsi"])
    volatility = float(data["volatility"])

    # ======================================================
    # SCORE
    # ======================================================

    score_result = calculate_score_details(
        data
    )

    score = score_result["score"]

    classification = (
        score_result["classification"]
    )

    signal = score_result["signal"]

    breakdown = score_result["breakdown"]

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
    # QUALIFICAÇÃO
    # ======================================================

    qualification = qualify_signal(
        score,
        trend,
        risk,
    )

    signal_level = qualification["level"]

    qualified_signal = qualification["signal"]

    signal_icon = qualification["icon"]

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

    # ------------------------------------------------------
    # Risco
    # ------------------------------------------------------

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
    # RESUMO EXECUTIVO
    # ======================================================

    executive_summary = generate_executive_summary(
        asset="Ativo",
        score=score,
        classification=classification,
        trend=trend,
        risk=risk,
        recommendation=recommendation,
        rsi_status=rsi_status,
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

        "qualified_signal":
            qualified_signal,

        "signal_level":
            signal_level,

        "signal_icon":
            signal_icon,

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

        "executive_summary":
            executive_summary,
    }
