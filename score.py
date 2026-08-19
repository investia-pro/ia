"""
InvestIA PRO
Motor de Score

Versão: v0.6
Fase: 2.9.7 - Score Robusto e Explicável
"""

from config import (
    BUY_SCORE,
    SELL_SCORE,
    RSI_OVERSOLD,
    RSI_OVERBOUGHT,
)


# ==========================================================
# LIMITAÇÃO DO SCORE
# ==========================================================

def clamp_score(score):
    """
    Mantém o Score entre 0 e 100.
    """

    try:

        score = float(score)

    except (
        TypeError,
        ValueError,
    ):

        return 50

    return max(
        0,
        min(
            100,
            int(
                round(
                    score
                )
            ),
        ),
    )


# ==========================================================
# CONVERSÃO SEGURA
# ==========================================================

def safe_float(
    value,
):
    """
    Converte valores numéricos com segurança.
    """

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
# VALIDAÇÃO
# ==========================================================

def validate_score_data(
    data,
):
    """
    Valida os dados necessários para o Score.
    """

    if data is None:

        return False

    if not isinstance(
        data,
        dict,
    ):

        return False

    required = [
        "price",
        "ma21",
        "ma200",
        "rsi",
    ]

    for field in required:

        if field not in data:

            return False

        if data[field] is None:

            return False

    return True


# ==========================================================
# CONTRIBUIÇÃO DA MA21
# ==========================================================

def calculate_ma21_component(
    price,
    ma21,
):
    """
    Calcula a contribuição da MA21.

    Acima da MA21:
        +10

    Abaixo da MA21:
        -10

    Igual:
        0
    """

    price = safe_float(
        price
    )

    ma21 = safe_float(
        ma21
    )

    if price is None or ma21 is None:

        return {

            "points": 0,

            "signal":
                "Indisponível",

            "reason":
                "MA21 não disponível.",
        }

    if price > ma21:

        return {

            "points": 10,

            "signal":
                "Positivo",

            "reason":
                "Preço acima da MA21.",
        }

    if price < ma21:

        return {

            "points": -10,

            "signal":
                "Negativo",

            "reason":
                "Preço abaixo da MA21.",
        }

    return {

        "points": 0,

        "signal":
            "Neutro",

        "reason":
            "Preço alinhado à MA21.",
    }


# ==========================================================
# CONTRIBUIÇÃO DA MA200
# ==========================================================

def calculate_ma200_component(
    price,
    ma200,
):
    """
    Calcula a contribuição da MA200.

    Acima da MA200:
        +20

    Abaixo da MA200:
        -20

    Igual:
        0
    """

    price = safe_float(
        price
    )

    ma200 = safe_float(
        ma200
    )

    if price is None or ma200 is None:

        return {

            "points": 0,

            "signal":
                "Indisponível",

            "reason":
                "MA200 não disponível.",
        }

    if price > ma200:

        return {

            "points": 20,

            "signal":
                "Positivo",

            "reason":
                "Preço acima da MA200.",
        }

    if price < ma200:

        return {

            "points": -20,

            "signal":
                "Negativo",

            "reason":
                "Preço abaixo da MA200.",
        }

    return {

        "points": 0,

        "signal":
            "Neutro",

        "reason":
            "Preço alinhado à MA200.",
    }


# ==========================================================
# CONTRIBUIÇÃO DO RSI
# ==========================================================

def calculate_rsi_component(
    rsi,
):
    """
    Calcula a contribuição do RSI.

    RSI <= sobrevenda:
        +10

    RSI >= sobrecompra:
        -10

    Região intermediária:
        0
    """

    rsi = safe_float(
        rsi
    )

    if rsi is None:

        return {

            "points": 0,

            "signal":
                "Indisponível",

            "reason":
                "RSI não disponível.",
        }

    if rsi <= RSI_OVERSOLD:

        return {

            "points": 10,

            "signal":
                "Positivo",

            "reason":
                "RSI em região de sobrevenda.",
        }

    if rsi >= RSI_OVERBOUGHT:

        return {

            "points": -10,

            "signal":
                "Negativo",

            "reason":
                "RSI em região de sobrecompra.",
        }

    return {

        "points": 0,

        "signal":
            "Neutro",

        "reason":
            "RSI em região neutra.",
    }


# ==========================================================
# BREAKDOWN COMPLETO
# ==========================================================

def get_score_breakdown(
    data,
):
    """
    Calcula a composição completa do Score.

    Base:
        50 pontos

    MA21:
        +/- 10

    MA200:
        +/- 20

    RSI:
        +/- 10

    Pontuação máxima:
        90

    Pontuação mínima:
        10
    """

    if not validate_score_data(
        data
    ):

        raise ValueError(
            "Dados insuficientes para calcular o Score InvestIA."
        )

    price = safe_float(
        data.get(
            "price"
        )
    )

    ma21 = safe_float(
        data.get(
            "ma21"
        )
    )

    ma200 = safe_float(
        data.get(
            "ma200"
        )
    )

    rsi = safe_float(
        data.get(
            "rsi"
        )
    )

    # ======================================================
    # BASE
    # ======================================================

    base = 50

    # ======================================================
    # COMPONENTES
    # ======================================================

    ma21_data = calculate_ma21_component(
        price,
        ma21,
    )

    ma200_data = calculate_ma200_component(
        price,
        ma200,
    )

    rsi_data = calculate_rsi_component(
        rsi
    )

    # ======================================================
    # SCORE BRUTO
    # ======================================================

    raw_score = (
        base
        + ma21_data["points"]
        + ma200_data["points"]
        + rsi_data["points"]
    )

    # ======================================================
    # SCORE FINAL
    # ======================================================

    final_score = clamp_score(
        raw_score
    )

    # ======================================================
    # RETORNO
    # ======================================================

    return {

        "base":
            base,

        "ma21":
            ma21_data,

        "ma200":
            ma200_data,

        "rsi":
            rsi_data,

        "raw_score":
            raw_score,

        "score":
            final_score,
    }


# ==========================================================
# SCORE PRINCIPAL
# ==========================================================

def calculate_investia_score(
    data,
):
    """
    Calcula somente o Score InvestIA.
    """

    breakdown = get_score_breakdown(
        data
    )

    return breakdown[
        "score"
    ]


# ==========================================================
# CLASSIFICAÇÃO
# ==========================================================

def classify_score(
    score,
):
    """
    Classifica o Score InvestIA.

    >= 80:
        FORTE

    >= 65:
        BOM

    >= 50:
        NEUTRO

    >= 35:
        FRACO

    < 35:
        MUITO FRACO
    """

    score = clamp_score(
        score
    )

    if score >= 80:

        return "FORTE"

    if score >= 65:

        return "BOM"

    if score >= 50:

        return "NEUTRO"

    if score >= 35:

        return "FRACO"

    return "MUITO FRACO"


# ==========================================================
# SINAL
# ==========================================================

def classify_signal(
    score,
):
    """
    Define o sinal do Score.
    """

    score = clamp_score(
        score
    )

    if score >= BUY_SCORE:

        return "POSITIVO"

    if score <= SELL_SCORE:

        return "NEGATIVO"

    return "NEUTRO"


# ==========================================================
# NÍVEL DO SINAL
# ==========================================================

def get_signal_level(
    score,
):
    """
    Define o nível qualitativo do sinal.
    """

    score = clamp_score(
        score
    )

    if score >= 80:

        return "Muito forte"

    if score >= BUY_SCORE:

        return "Forte"

    if score <= 20:

        return "Muito fraco"

    if score <= SELL_SCORE:

        return "Fraco"

    return "Aguardar"


# ==========================================================
# ÍCONE DO SINAL
# ==========================================================

def get_signal_icon(
    score,
):
    """
    Retorna o ícone correspondente ao Score.
    """

    score = clamp_score(
        score
    )

    if score >= 80:

        return "🟢"

    if score >= BUY_SCORE:

        return "🟢"

    if score <= SELL_SCORE:

        return "🔴"

    return "🟡"


# ==========================================================
# SCORE COMPLETO
# ==========================================================

def calculate_score_details(
    data,
):
    """
    Retorna o Score completo com:

    - Score
    - Classificação
    - Sinal
    - Nível
    - Ícone
    - Breakdown
    """

    breakdown = get_score_breakdown(
        data
    )

    score = breakdown[
        "score"
    ]

    return {

        "score":
            score,

        "classification":
            classify_score(
                score
            ),

        "signal":
            classify_signal(
                score
            ),

        "signal_level":
            get_signal_level(
                score
            ),

        "signal_icon":
            get_signal_icon(
                score
            ),

        "breakdown":
            breakdown,
    }


# ==========================================================
# SCORE COM RESUMO
# ==========================================================

def get_score_summary(
    data,
):
    """
    Retorna um resumo simplificado do Score.
    """

    details = calculate_score_details(
        data
    )

    return {

        "score":
            details[
                "score"
            ],

        "classification":
            details[
                "classification"
            ],

        "signal":
            details[
                "signal"
            ],

        "signal_level":
            details[
                "signal_level"
            ],

        "signal_icon":
            details[
                "signal_icon"
            ],
    }
