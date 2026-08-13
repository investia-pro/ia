"""
InvestIA PRO
Motor de Análise

Versão: v0.6
Fase: 2.7.1 - Motor de Risco e Sinal
"""

from score import calculate_investia_score


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def safe_float(value, default=0.0):
    """
    Converte valores numéricos com segurança.
    """

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_text(value, default="Neutro"):
    """
    Normaliza textos utilizados na análise.
    """

    if value is None:
        return default

    text = str(value).strip()

    if not text:
        return default

    return text


def classify_score(score):
    """
    Classificação qualitativa do Score InvestIA.
    """

    if score >= 80:
        return "MUITO FORTE"

    if score >= 65:
        return "FORTE"

    if score >= 50:
        return "NEUTRO"

    if score >= 35:
        return "FRACO"

    return "MUITO FRACO"


def classify_signal(score):
    """
    Define o sinal operacional principal.
    """

    if score >= 65:
        return "POSITIVO"

    if score <= 35:
        return "NEGATIVO"

    return "NEUTRO"


def classify_recommendation(score):
    """
    Define a recomendação operacional.
    """

    if score >= 75:
        return "Compra"

    if score >= 65:
        return "Compra Moderada"

    if score <= 25:
        return "Venda"

    if score <= 35:
        return "Venda Moderada"

    return "Aguardar"


def classify_risk(volatility):
    """
    Classifica o risco com base na volatilidade.
    """

    volatility = safe_float(volatility)

    if volatility < 0.015:
        return "Baixo"

    if volatility < 0.030:
        return "Moderado"

    return "Alto"


def risk_score(volatility):
    """
    Converte a volatilidade em uma escala de risco 0-100.

    Quanto maior o valor, maior o risco.
    """

    volatility = safe_float(volatility)

    if volatility <= 0:
        return 0

    score = volatility / 0.040 * 100

    return max(
        0,
        min(
            100,
            round(score),
        ),
    )


def calculate_trend(
    price,
    ma21,
    ma200,
):
    """
    Determina a tendência considerando
    preço x MA21 e preço x MA200.
    """

    price = safe_float(price)
    ma21 = safe_float(ma21)
    ma200 = safe_float(ma200)

    above_ma21 = price > ma21
    above_ma200 = price > ma200

    if above_ma21 and above_ma200:
        return "Positiva"

    if not above_ma21 and not above_ma200:
        return "Negativa"

    return "Moderada"


def calculate_rsi_status(rsi):
    """
    Classifica o RSI.
    """

    rsi = safe_float(rsi)

    if rsi <= 30:
        return "Sobrevendido"

    if rsi >= 70:
        return "Sobrecomprado"

    return "Neutro"


def build_alerts(
    score,
    risk,
    trend,
    rsi_status,
):
    """
    Identifica situações que exigem atenção.
    """

    alerts = []

    # ------------------------------------------------------
    # Score alto + risco alto
    # ------------------------------------------------------

    if score >= 65 and risk == "Alto":

        alerts.append(
            "Score favorável, porém com risco elevado."
        )


    # ------------------------------------------------------
    # Score baixo + risco baixo
    # ------------------------------------------------------

    if score <= 35 and risk == "Baixo":

        alerts.append(
            "Score desfavorável apesar do baixo risco."
        )


    # ------------------------------------------------------
    # Tendência positiva + sobrecompra
    # ------------------------------------------------------

    if (
        trend == "Positiva"
        and rsi_status == "Sobrecomprado"
    ):

        alerts.append(
            "Tendência positiva, mas RSI indica sobrecompra."
        )


    # ------------------------------------------------------
    # Tendência negativa + sobrevenda
    # ------------------------------------------------------

    if (
        trend == "Negativa"
        and rsi_status == "Sobrevendido"
    ):

        alerts.append(
            "Tendência negativa, mas RSI indica sobrevenda."
        )


    # ------------------------------------------------------
    # Ausência de alertas
    # ------------------------------------------------------

    if not alerts:

        alerts.append(
            "Nenhum alerta técnico relevante identificado."
        )


    return alerts


def build_qualified_signal(
    recommendation,
    risk,
):
    """
    Combina recomendação e risco em um sinal
    operacional mais informativo.
    """

    if recommendation == "Compra":

        if risk == "Alto":
            return "COMPRA COM ALTO RISCO"

        return "COMPRA"

    if recommendation == "Compra Moderada":

        if risk == "Alto":
            return "COMPRA MODERADA COM ALTO RISCO"

        return "COMPRA MODERADA"

    if recommendation == "Venda":

        if risk == "Alto":
            return "VENDA COM ALTO RISCO"

        return "VENDA"

    if recommendation == "Venda Moderada":

        if risk == "Alto":
            return "VENDA MODERADA COM ALTO RISCO"

        return "VENDA MODERADA"

    return "AGUARDAR"


def build_signal_level(
    score,
    risk,
):
    """
    Define o nível de confiança operacional.
    """

    if score >= 75 and risk != "Alto":
        return "Forte"

    if score >= 65 and risk == "Baixo":
        return "Forte"

    if score >= 65:
        return "Moderado"

    if score <= 35 and risk != "Alto":
        return "Forte"

    if score <= 35:
        return "Moderado"

    return "Neutro"


def build_signal_icon(
    recommendation,
):
    """
    Ícone correspondente à recomendação.
    """

    if recommendation in (
        "Compra",
        "Compra Moderada",
    ):
        return "🟢"

    if recommendation in (
        "Venda",
        "Venda Moderada",
    ):
        return "🔴"

    return "🟡"


def build_executive_summary(
    asset,
    price,
    score,
    classification,
    trend,
    recommendation,
    risk,
    rsi_status,
):
    """
    Gera o resumo executivo da análise.
    """

    asset = normalize_text(
        asset,
        "Ativo",
    )

    price = safe_float(price)
    score = safe_float(score)

    summary = (
        f"{asset} apresenta Score InvestIA de "
        f"{score:.0f}/100, classificação "
        f"{classification.lower()}. "
    )

    summary += (
        f"A tendência é {trend.lower()}, "
        f"com recomendação de "
        f"{recommendation.lower()}. "
    )

    summary += (
        f"O risco atual é {risk.lower()} "
        f"e o RSI está em condição "
        f"{rsi_status.lower()}."
    )

    return summary


# ==========================================================
# MOTOR PRINCIPAL
# ==========================================================

def analyze_asset(
    data,
    asset=None,
):
    """
    Executa a análise completa do ativo.

    Parâmetros
    ----------
    data : dict
        Indicadores técnicos.

    asset : str, opcional
        Código do ativo.

    Retorno
    -------
    dict
        Resultado completo da análise.
    """

    if not isinstance(data, dict):
        raise ValueError(
            "Os dados para análise devem ser um dicionário."
        )


    # ======================================================
    # INDICADORES
    # ======================================================

    price = safe_float(
        data.get("price")
    )

    ma21 = safe_float(
        data.get("ma21")
    )

    ma200 = safe_float(
        data.get("ma200")
    )

    rsi = safe_float(
        data.get("rsi")
    )

    volatility = safe_float(
        data.get("volatility")
    )


    # ======================================================
    # SCORE INVESTIA
    # ======================================================

    try:

        score_result = calculate_investia_score(
            data
        )

    except TypeError:

        score_result = calculate_investia_score(
            price=price,
            ma21=ma21,
            ma200=ma200,
            rsi=rsi,
            volatility=volatility,
        )


    # ======================================================
    # COMPATIBILIDADE COM score.py
    # ======================================================

    if isinstance(
        score_result,
        dict,
    ):

        score = score_result.get(
            "score",
            score_result.get(
                "final_score",
                50,
            ),
        )

        breakdown = score_result.get(
            "breakdown",
            {},
        )

    else:

        score = score_result

        breakdown = {}


    score = safe_float(
        score,
        50,
    )

    score = max(
        0,
        min(
            100,
            round(score),
        ),
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
    # TENDÊNCIA
    # ======================================================

    trend = calculate_trend(
        price,
        ma21,
        ma200,
    )


    # ======================================================
    # RSI
    # ======================================================

    rsi_status = calculate_rsi_status(
        rsi
    )


    # ======================================================
    # RISCO
    # ======================================================

    risk = classify_risk(
        volatility
    )


    risk_points = risk_score(
        volatility
    )


    # ======================================================
    # RECOMENDAÇÃO
    # ======================================================

    recommendation = classify_recommendation(
        score
    )


    # ======================================================
    # SINAL QUALIFICADO
    # ======================================================

    qualified_signal = build_qualified_signal(
        recommendation,
        risk,
    )


    # ======================================================
    # NÍVEL DO SINAL
    # ======================================================

    signal_level = build_signal_level(
        score,
        risk,
    )


    # ======================================================
    # ÍCONE
    # ======================================================

    signal_icon = build_signal_icon(
        recommendation
    )


    # ======================================================
    # ALERTAS
    # ======================================================

    alerts = build_alerts(
        score,
        risk,
        trend,
        rsi_status,
    )


    # ======================================================
    # RESUMO EXECUTIVO
    # ======================================================

    executive_summary = build_executive_summary(
        asset,
        price,
        score,
        classification,
        trend,
        recommendation,
        risk,
        rsi_status,
    )


    # ======================================================
    # RESULTADO FINAL
    # ======================================================

    return {

        "asset": asset,

        "price": price,

        "score": score,

        "classification": classification,

        "signal": signal,

        "qualified_signal": qualified_signal,

        "signal_level": signal_level,

        "signal_icon": signal_icon,

        "trend": trend,

        "recommendation": recommendation,

        "risk": risk,

        "risk_score": risk_points,

        "rsi_status": rsi_status,

        "alerts": alerts,

        "reasons": alerts,

        "breakdown": breakdown,

        "executive_summary": executive_summary,

    }
