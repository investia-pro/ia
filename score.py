"""
InvestIA PRO
Motor de Pontuação

Versão: v0.6
Fase: 2.1 - Consolidação do Score 2.0
"""

from config import (
    RSI_OVERSOLD,
    RSI_OVERBOUGHT,
)


# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

MIN_SCORE = 0
MAX_SCORE = 100

WEIGHT_RSI = 0.15
WEIGHT_MA21 = 0.15
WEIGHT_MA200 = 0.20
WEIGHT_TREND = 0.20
WEIGHT_RISK = 0.15
WEIGHT_TECHNICAL = 0.15


# ==========================================================
# FUNÇÃO AUXILIAR
# ==========================================================

def clamp(value, minimum=0, maximum=100):
    """
    Mantém o valor dentro do intervalo definido.
    """

    try:
        value = float(value)

    except (TypeError, ValueError):
        return minimum

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


# ==========================================================
# SCORE RSI
# ==========================================================

def score_rsi(rsi):
    """
    Converte o RSI para uma pontuação de 0 a 100.
    """

    try:
        rsi = float(rsi)

    except (TypeError, ValueError):
        return 50.0

    if rsi <= RSI_OVERSOLD:
        return 85.0

    if rsi >= RSI_OVERBOUGHT:
        return 25.0

    intervalo = (
        RSI_OVERBOUGHT
        - RSI_OVERSOLD
    )

    if intervalo <= 0:
        return 50.0

    score = 85 - (
        (rsi - RSI_OVERSOLD)
        * 60
        / intervalo
    )

    return clamp(score)


# ==========================================================
# SCORE MA21
# ==========================================================

def score_ma21(price, ma21):
    """
    Avalia a posição do preço em relação à MA21.
    """

    try:
        price = float(price)
        ma21 = float(ma21)

    except (TypeError, ValueError):
        return 50.0

    if ma21 <= 0:
        return 50.0

    distance = (
        (price - ma21)
        / ma21
    ) * 100

    if distance >= 5:
        return 85.0

    if distance > 0:

        return clamp(
            65 + (
                distance * 4
            )
        )

    if distance <= -5:
        return 20.0

    return clamp(
        65 + (
            distance * 9
        )
    )


# ==========================================================
# SCORE MA200
# ==========================================================

def score_ma200(price, ma200):
    """
    Avalia a posição do preço em relação à MA200.
    """

    try:
        price = float(price)
        ma200 = float(ma200)

    except (TypeError, ValueError):
        return 50.0

    if ma200 <= 0:
        return 50.0

    distance = (
        (price - ma200)
        / ma200
    ) * 100

    if distance >= 10:
        return 95.0

    if distance > 0:

        return clamp(
            65 + (
                distance * 3
            )
        )

    if distance <= -10:
        return 15.0

    return clamp(
        65 + (
            distance * 5
        )
    )


# ==========================================================
# SCORE DE TENDÊNCIA
# ==========================================================

def score_trend(
    price,
    ma21,
    ma200,
):
    """
    Avalia a tendência utilizando:

    - preço
    - MA21
    - MA200
    """

    try:
        price = float(price)
        ma21 = float(ma21)
        ma200 = float(ma200)

    except (TypeError, ValueError):
        return 50.0

    # Tendência fortemente positiva
    if (
        price > ma21
        and price > ma200
        and ma21 > ma200
    ):
        return 100.0

    # Tendência positiva
    if (
        price > ma21
        and price > ma200
    ):
        return 85.0

    # Tendência fortemente negativa
    if (
        price < ma21
        and price < ma200
        and ma21 < ma200
    ):
        return 10.0

    # Tendência negativa
    if (
        price < ma21
        and price < ma200
    ):
        return 25.0

    # Tendência indefinida
    return 50.0


# ==========================================================
# SCORE DE RISCO
# ==========================================================

def score_risk(volatility):
    """
    Converte a volatilidade em score de controle de risco.

    Menor volatilidade = maior score de controle.
    """

    try:
        volatility = float(
            volatility
        )

    except (TypeError, ValueError):
        return 50.0

    if volatility <= 0.01:
        return 95.0

    if volatility <= 0.015:
        return 85.0

    if volatility <= 0.02:
        return 75.0

    if volatility <= 0.03:
        return 60.0

    if volatility <= 0.04:
        return 45.0

    if volatility <= 0.06:
        return 30.0

    return 15.0


# ==========================================================
# SCORE TÉCNICO
# ==========================================================

def score_technical(
    rsi_score,
    ma21_score,
    ma200_score,
):
    """
    Consolida RSI, MA21 e MA200.
    """

    scores = [
        clamp(rsi_score),
        clamp(ma21_score),
        clamp(ma200_score),
    ]

    return clamp(
        sum(scores)
        / len(scores)
    )


# ==========================================================
# SCORE FINAL
# ==========================================================

def calculate_final_score(
    rsi_score,
    ma21_score,
    ma200_score,
    trend_score,
    risk_score,
    technical_score,
):
    """
    Calcula o Score InvestIA final.
    """

    score = (

        rsi_score
        * WEIGHT_RSI

        +

        ma21_score
        * WEIGHT_MA21

        +

        ma200_score
        * WEIGHT_MA200

        +

        trend_score
        * WEIGHT_TREND

        +

        risk_score
        * WEIGHT_RISK

        +

        technical_score
        * WEIGHT_TECHNICAL

    )

    return round(
        clamp(score),
        0,
    )


# ==========================================================
# CLASSIFICAÇÃO
# ==========================================================

def classify_score(score):
    """
    Classificação do Score InvestIA.
    """

    score = clamp(score)

    if score >= 80:
        return "MUITO FORTE"

    if score >= 65:
        return "FORTE"

    if score >= 50:
        return "NEUTRO"

    if score >= 35:
        return "FRACO"

    return "MUITO FRACO"


# ==========================================================
# SINAL
# ==========================================================

def generate_signal(score):
    """
    Gera o sinal operacional.
    """

    score = clamp(score)

    if score >= 65:
        return "POSITIVO"

    if score >= 50:
        return "NEUTRO"

    return "NEGATIVO"


# ==========================================================
# RECOMENDAÇÃO
# ==========================================================

def generate_recommendation(score):
    """
    Gera a recomendação baseada no Score.
    """

    score = clamp(score)

    if score >= 80:
        return "Compra Forte"

    if score >= 65:
        return "Compra Moderada"

    if score >= 50:
        return "Aguardar"

    if score >= 35:
        return "Aguardar"

    return "Venda"


# ==========================================================
# SCORE PRINCIPAL
# ==========================================================

def calculate_score(indicators):
    """
    Calcula o Score InvestIA 2.0.

    Entrada:

        {
            "price": ...,
            "rsi": ...,
            "ma21": ...,
            "ma200": ...,
            "volatility": ...
        }

    Retorna todos os componentes utilizados
    pela aplicação.
    """

    if not isinstance(
        indicators,
        dict,
    ):

        raise TypeError(
            "indicators deve ser um dicionário."
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
        if field not in indicators
        or indicators[field] is None
    ]

    if missing:

        raise ValueError(
            "Indicadores ausentes: "
            + ", ".join(missing)
        )


    # ------------------------------------------------------
    # COMPONENTES
    # ------------------------------------------------------

    rsi_score = score_rsi(
        indicators["rsi"]
    )

    ma21_score = score_ma21(
        indicators["price"],
        indicators["ma21"],
    )

    ma200_score = score_ma200(
        indicators["price"],
        indicators["ma200"],
    )

    trend_score = score_trend(
        indicators["price"],
        indicators["ma21"],
        indicators["ma200"],
    )

    risk_score = score_risk(
        indicators["volatility"]
    )

    technical_score = score_technical(
        rsi_score,
        ma21_score,
        ma200_score,
    )


    # ------------------------------------------------------
    # SCORE FINAL
    # ------------------------------------------------------

    score = calculate_final_score(
        rsi_score,
        ma21_score,
        ma200_score,
        trend_score,
        risk_score,
        technical_score,
    )


    # ------------------------------------------------------
    # CLASSIFICAÇÃO
    # ------------------------------------------------------

    classification = classify_score(
        score
    )

    signal = generate_signal(
        score
    )

    recommendation = generate_recommendation(
        score
    )


    # ------------------------------------------------------
    # RETORNO
    # ------------------------------------------------------

    return {

        "score":
            score,

        "classification":
            classification,

        "signal":
            signal,

        "recommendation":
            recommendation,

        "rsi_score":
            round(
                rsi_score,
                0,
            ),

        "ma21_score":
            round(
                ma21_score,
                0,
            ),

        "ma200_score":
            round(
                ma200_score,
                0,
            ),

        "trend_score":
            round(
                trend_score,
                0,
            ),

        "risk_score":
            round(
                risk_score,
                0,
            ),

        "technical_score":
            round(
                technical_score,
                0,
            ),
    }


# ==========================================================
# COMPATIBILIDADE COM VERSÕES ANTERIORES
# ==========================================================

def calculate_investia_score(
    indicators
):
    """
    Função de compatibilidade.

    Algumas versões do analysis.py utilizam
    calculate_investia_score().

    Mantemos esse nome para evitar
    ImportError durante a transição
    para o Score 2.0.
    """

    return calculate_score(
        indicators
    )
