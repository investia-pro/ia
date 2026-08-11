"""
InvestIA PRO
Motor de Análise

Versão: v0.6
Fase: 2.2 - Integração do Score 2.0
"""

from score import calculate_investia_score


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def _get_trend(score_data):
    """
    Determina a tendência principal do ativo.
    """

    trend_score = score_data.get(
        "trend_score",
        50,
    )

    if trend_score >= 80:
        return "Positiva"

    if trend_score >= 60:
        return "Levemente Positiva"

    if trend_score >= 40:
        return "Neutra"

    if trend_score >= 20:
        return "Levemente Negativa"

    return "Negativa"


def _get_risk(score_data):
    """
    Determina o nível de risco.

    risk_score representa controle de risco:
    quanto maior, menor o risco observado.
    """

    risk_score = score_data.get(
        "risk_score",
        50,
    )

    if risk_score >= 80:
        return "Baixo"

    if risk_score >= 60:
        return "Moderado"

    if risk_score >= 40:
        return "Alto"

    return "Muito Alto"


def _build_reasons(
    indicators,
    score_data,
):
    """
    Gera as justificativas da análise.
    """

    reasons = []

    price = indicators["price"]
    ma21 = indicators["ma21"]
    ma200 = indicators["ma200"]
    rsi = indicators["rsi"]

    # ======================================================
    # PREÇO X MA21
    # ======================================================

    if price > ma21:

        reasons.append(
            "Preço acima da média móvel de 21 períodos."
        )

    else:

        reasons.append(
            "Preço abaixo da média móvel de 21 períodos."
        )

    # ======================================================
    # PREÇO X MA200
    # ======================================================

    if price > ma200:

        reasons.append(
            "Preço acima da média móvel de 200 períodos."
        )

    else:

        reasons.append(
            "Preço abaixo da média móvel de 200 períodos."
        )

    # ======================================================
    # RELAÇÃO MA21 X MA200
    # ======================================================

    if ma21 > ma200:

        reasons.append(
            "MA21 acima da MA200, indicando estrutura "
            "de tendência de longo prazo favorável."
        )

    elif ma21 < ma200:

        reasons.append(
            "MA21 abaixo da MA200, indicando estrutura "
            "de tendência de longo prazo desfavorável."
        )

    else:

        reasons.append(
            "MA21 e MA200 estão praticamente no mesmo nível."
        )

    # ======================================================
    # RSI
    # ======================================================

    if rsi <= 30:

        reasons.append(
            "RSI em região de sobrevenda."
        )

    elif rsi >= 70:

        reasons.append(
            "RSI em região de sobrecompra."
        )

    else:

        reasons.append(
            "RSI em região intermediária."
        )

    # ======================================================
    # SCORE
    # ======================================================

    score = score_data.get(
        "score",
        50,
    )

    if score >= 80:

        reasons.append(
            "Score InvestIA indica forte predominância "
            "de fatores favoráveis."
        )

    elif score >= 65:

        reasons.append(
            "Score InvestIA indica predominância "
            "de fatores favoráveis."
        )

    elif score >= 50:

        reasons.append(
            "Score InvestIA indica equilíbrio entre "
            "fatores positivos e negativos."
        )

    elif score >= 35:

        reasons.append(
            "Score InvestIA indica predominância "
            "de fatores desfavoráveis."
        )

    else:

        reasons.append(
            "Score InvestIA indica forte predominância "
            "de fatores desfavoráveis."
        )

    return reasons


# ==========================================================
# ANÁLISE PRINCIPAL
# ==========================================================

def analyze_asset(data):
    """
    Analisa um ativo utilizando os indicadores técnicos
    e o Score InvestIA 2.0.

    Parâmetro
    ---------
    data : dict

        Deve conter:

        price
        rsi
        ma21
        ma200
        volatility

    Retorno
    -------

    Dicionário completo utilizado pelo app.py.
    """

    if not isinstance(
        data,
        dict,
    ):

        raise TypeError(
            "data deve ser um dicionário."
        )

    required = [
        "price",
        "rsi",
        "ma21",
        "ma200",
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
            "Dados necessários ausentes: "
            + ", ".join(missing)
        )

    # ======================================================
    # SCORE 2.0
    # ======================================================

    score_data = calculate_investia_score(
        data
    )

    # ======================================================
    # INTERPRETAÇÃO
    # ======================================================

    score = score_data[
        "score"
    ]

    classification = score_data[
        "classification"
    ]

    signal = score_data[
        "signal"
    ]

    recommendation = score_data[
        "recommendation"
    ]

    # ======================================================
    # TENDÊNCIA
    # ======================================================

    trend = _get_trend(
        score_data
    )

    # ======================================================
    # RISCO
    # ======================================================

    risk = _get_risk(
        score_data
    )

    # ======================================================
    # JUSTIFICATIVAS
    # ======================================================

    reasons = _build_reasons(
        data,
        score_data,
    )

    # ======================================================
    # RETORNO
    # ======================================================

    return {

        # --------------------------------------------------
        # SCORE
        # --------------------------------------------------

        "score":
            score,

        "classification":
            classification,

        "signal":
            signal,

        "recommendation":
            recommendation,

        # --------------------------------------------------
        # INTERPRETAÇÃO
        # --------------------------------------------------

        "trend":
            trend,

        "risk":
            risk,

        "reasons":
            reasons,

        # --------------------------------------------------
        # COMPONENTES DO SCORE
        # --------------------------------------------------

        "rsi_score":
            score_data[
                "rsi_score"
            ],

        "ma21_score":
            score_data[
                "ma21_score"
            ],

        "ma200_score":
            score_data[
                "ma200_score"
            ],

        "trend_score":
            score_data[
                "trend_score"
            ],

        "risk_score":
            score_data[
                "risk_score"
            ],

        "technical_score":
            score_data[
                "technical_score"
            ],
    }
