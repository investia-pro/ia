"""
InvestIA PRO
Motor de Score Quantitativo

Versão: v0.6
Fase: 1.5

Responsável por transformar os indicadores técnicos
em uma pontuação de 0 a 100.

Este módulo não acessa dados externos e não possui
dependência do Streamlit.
"""

from typing import Any


# ==========================================================
# CONFIGURAÇÃO DO SCORE
# ==========================================================

WEIGHTS = {
    "rsi": 0.25,
    "ma21": 0.20,
    "ma200": 0.25,
    "trend": 0.20,
    "risk": 0.10,
}


# ==========================================================
# LIMITES
# ==========================================================

MIN_SCORE = 0
MAX_SCORE = 100


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def _clamp(
    value: float,
    minimum: float = MIN_SCORE,
    maximum: float = MAX_SCORE,
) -> float:

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


def _safe_float(
    value: Any,
) -> float | None:

    try:

        if value is None:
            return None

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return None


# ==========================================================
# SCORE DO RSI
# ==========================================================

def calculate_rsi_score(
    rsi: float,
) -> float:

    rsi = _safe_float(rsi)

    if rsi is None:
        return 50.0

    if rsi < 20:
        score = 45

    elif rsi < 30:
        score = 60

    elif rsi < 40:
        score = 65

    elif rsi <= 60:
        score = 55

    elif rsi <= 70:
        score = 75

    elif rsi <= 80:
        score = 55

    else:
        score = 40

    return float(
        _clamp(score)
    )


# ==========================================================
# SCORE DA MA21
# ==========================================================

def calculate_ma21_score(
    price: float,
    ma21: float,
) -> float:

    price = _safe_float(price)
    ma21 = _safe_float(ma21)

    if price is None or ma21 is None:
        return 50.0

    if ma21 <= 0:
        return 50.0

    difference = (
        (price - ma21)
        / ma21
    ) * 100

    if difference >= 5:
        score = 90

    elif difference >= 2:
        score = 80

    elif difference >= 0:
        score = 65

    elif difference >= -2:
        score = 45

    elif difference >= -5:
        score = 30

    else:
        score = 15

    return float(
        _clamp(score)
    )


# ==========================================================
# SCORE DA MA200
# ==========================================================

def calculate_ma200_score(
    price: float,
    ma200: float,
) -> float:

    price = _safe_float(price)
    ma200 = _safe_float(ma200)

    if price is None or ma200 is None:
        return 50.0

    if ma200 <= 0:
        return 50.0

    difference = (
        (price - ma200)
        / ma200
    ) * 100

    if difference >= 10:
        score = 95

    elif difference >= 5:
        score = 85

    elif difference >= 0:
        score = 70

    elif difference >= -5:
        score = 45

    elif difference >= -10:
        score = 25

    else:
        score = 10

    return float(
        _clamp(score)
    )


# ==========================================================
# SCORE DE TENDÊNCIA
# ==========================================================

def calculate_trend_score(
    price: float,
    ma21: float,
    ma200: float,
) -> float:

    price = _safe_float(price)
    ma21 = _safe_float(ma21)
    ma200 = _safe_float(ma200)

    if (
        price is None
        or ma21 is None
        or ma200 is None
    ):
        return 50.0

    score = 50.0

    # ------------------------------------------------------
    # Preço x MA21
    # ------------------------------------------------------

    if price > ma21:

        score += 15

    elif price < ma21:

        score -= 15

    # ------------------------------------------------------
    # Preço x MA200
    # ------------------------------------------------------

    if price > ma200:

        score += 20

    elif price < ma200:

        score -= 20

    # ------------------------------------------------------
    # MA21 x MA200
    # ------------------------------------------------------

    if ma21 > ma200:

        score += 15

    elif ma21 < ma200:

        score -= 15

    return float(
        _clamp(score)
    )


# ==========================================================
# SCORE DE RISCO
# ==========================================================

def calculate_risk_score(
    volatility: float,
) -> float:

    volatility = _safe_float(
        volatility
    )

    if volatility is None:
        return 50.0

    # Aceita:
    #
    # 0.0169 = 1,69%
    #
    # ou
    #
    # 1.69 = 1,69%

    if volatility > 1:

        volatility = volatility / 100

    if volatility <= 0.01:

        score = 90

    elif volatility <= 0.02:

        score = 75

    elif volatility <= 0.03:

        score = 60

    elif volatility <= 0.04:

        score = 45

    elif volatility <= 0.06:

        score = 30

    else:

        score = 15

    return float(
        _clamp(score)
    )


# ==========================================================
# CLASSIFICAÇÃO DO SCORE
# ==========================================================

def classify_score(
    score: float,
) -> str:
    """
    Classificação oficial do Score InvestIA 2.0.

    80–100  = MUITO FORTE
    70–79   = FORTE
    60–69   = MODERADO
    45–59   = NEUTRO
    30–44   = FRACO
    0–29    = MUITO FRACO
    """

    score = _safe_float(score)

    if score is None:

        return "INDEFINIDO"

    if score >= 80:

        return "MUITO FORTE"

    if score >= 70:

        return "FORTE"

    if score >= 60:

        return "MODERADO"

    if score >= 45:

        return "NEUTRO"

    if score >= 30:

        return "FRACO"

    return "MUITO FRACO"


# ==========================================================
# SINAL
# ==========================================================

def classify_signal(
    score: float,
) -> str:
    """
    Interpretação operacional do Score.

    80–100  = MUITO POSITIVO
    70–79   = POSITIVO
    60–69   = POSITIVO MODERADO
    45–59   = NEUTRO
    30–44   = NEGATIVO MODERADO
    0–29    = MUITO NEGATIVO

    O sinal é uma interpretação quantitativa
    e não representa recomendação financeira individual.
    """

    score = _safe_float(score)

    if score is None:

        return "INDEFINIDO"

    if score >= 80:

        return "MUITO POSITIVO"

    if score >= 70:

        return "POSITIVO"

    if score >= 60:

        return "POSITIVO MODERADO"

    if score >= 45:

        return "NEUTRO"

    if score >= 30:

        return "NEGATIVO MODERADO"

    return "MUITO NEGATIVO"


# ==========================================================
# FUNDAMENTAÇÃO
# ==========================================================

def generate_reasons(
    price: float,
    ma21: float,
    ma200: float,
    rsi: float,
    volatility: float,
) -> list[str]:

    reasons = []

    price = _safe_float(price)
    ma21 = _safe_float(ma21)
    ma200 = _safe_float(ma200)
    rsi = _safe_float(rsi)
    volatility = _safe_float(volatility)

    # ------------------------------------------------------
    # MA21
    # ------------------------------------------------------

    if (
        price is not None
        and ma21 is not None
    ):

        if price > ma21:

            reasons.append(
                "Preço acima da média móvel de 21 períodos."
            )

        elif price < ma21:

            reasons.append(
                "Preço abaixo da média móvel de 21 períodos."
            )

    # ------------------------------------------------------
    # MA200
    # ------------------------------------------------------

    if (
        price is not None
        and ma200 is not None
    ):

        if price > ma200:

            reasons.append(
                "Preço acima da média móvel de 200 períodos."
            )

        elif price < ma200:

            reasons.append(
                "Preço abaixo da média móvel de 200 períodos."
            )

    # ------------------------------------------------------
    # RSI
    # ------------------------------------------------------

    if rsi is not None:

        if rsi < 30:

            reasons.append(
                "RSI em região de sobrevenda."
            )

        elif rsi < 40:

            reasons.append(
                "RSI indica possível recuperação."
            )

        elif rsi <= 60:

            reasons.append(
                "RSI em região neutra."
            )

        elif rsi <= 70:

            reasons.append(
                "RSI indica força compradora."
            )

        else:

            reasons.append(
                "RSI em região de sobrecompra."
            )

    # ------------------------------------------------------
    # Volatilidade
    # ------------------------------------------------------

    if volatility is not None:

        if volatility <= 0.02:

            reasons.append(
                "Volatilidade diária dentro de uma faixa moderada."
            )

        elif volatility <= 0.04:

            reasons.append(
                "Volatilidade diária relativamente elevada."
            )

        else:

            reasons.append(
                "Volatilidade diária elevada, indicando maior risco."
            )

    return reasons


# ==========================================================
# SCORE PRINCIPAL
# ==========================================================

def calculate_investia_score(
    indicators: dict,
) -> dict:

    if not isinstance(
        indicators,
        dict,
    ):

        raise TypeError(
            "indicators deve ser um dicionário."
        )

    price = indicators.get(
        "price"
    )

    rsi = indicators.get(
        "rsi"
    )

    ma21 = indicators.get(
        "ma21"
    )

    ma200 = indicators.get(
        "ma200"
    )

    volatility = indicators.get(
        "volatility"
    )

    # ======================================================
    # SCORES INDIVIDUAIS
    # ======================================================

    rsi_score = calculate_rsi_score(
        rsi
    )

    ma21_score = calculate_ma21_score(
        price,
        ma21,
    )

    ma200_score = calculate_ma200_score(
        price,
        ma200,
    )

    trend_score = calculate_trend_score(
        price,
        ma21,
        ma200,
    )

    risk_score = calculate_risk_score(
        volatility
    )

    # ======================================================
    # SCORE TÉCNICO
    # ======================================================

    technical_score = (
        (
            rsi_score
            * WEIGHTS["rsi"]
        )
        +
        (
            ma21_score
            * WEIGHTS["ma21"]
        )
        +
        (
            ma200_score
            * WEIGHTS["ma200"]
        )
    )

    # ======================================================
    # SCORE FINAL
    # ======================================================

    final_score = (
        technical_score
        +
        (
            trend_score
            * WEIGHTS["trend"]
        )
        +
        (
            risk_score
            * WEIGHTS["risk"]
        )
    )

    final_score = round(
        _clamp(final_score),
        2,
    )

    # ======================================================
    # CLASSIFICAÇÃO
    # ======================================================

    classification = classify_score(
        final_score
    )

    signal = classify_signal(
        final_score
    )

    # ======================================================
    # FUNDAMENTAÇÃO
    # ======================================================

    reasons = generate_reasons(
        price,
        ma21,
        ma200,
        rsi,
        volatility,
    )

    # ======================================================
    # RESULTADO
    # ======================================================

    return {

        "score": final_score,

        "classification": classification,

        "signal": signal,

        "rsi": round(
            rsi_score,
            2,
        ),

        "ma21": round(
            ma21_score,
            2,
        ),

        "ma200": round(
            ma200_score,
            2,
        ),

        "trend": round(
            trend_score,
            2,
        ),

        "risk": round(
            risk_score,
            2,
        ),

        "technical": round(
            technical_score,
            2,
        ),

        "reasons": reasons,
    }
