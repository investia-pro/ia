"""
InvestIA PRO
Motor de Score

Versão: v0.6
Fase: 2.9.6 - Estabilidade e Validação de Dados
"""

from config import (
    BUY_SCORE,
    SELL_SCORE,
    RSI_OVERSOLD,
    RSI_OVERBOUGHT,
)

from utils import (
    is_valid_number,
    safe_float,
    validate_indicators,
)


# ==========================================================
# LIMITAÇÃO DO SCORE
# ==========================================================

def clamp_score(score):
    """
    Mantém o Score entre 0 e 100.

    Valores inválidos não são convertidos
    artificialmente para um Score válido.
    """

    if not is_valid_number(score):
        return None

    return max(
        0,
        min(
            100,
            int(round(float(score))),
        ),
    )


# ==========================================================
# VALIDAÇÃO DOS DADOS DO SCORE
# ==========================================================

def validate_score_data(data):
    """
    Valida os dados necessários para o cálculo
    do Score InvestIA.

    O Score exige:

        price
        ma21
        ma200
        rsi

    A volatilidade não participa diretamente
    do cálculo do Score.
    """

    if not isinstance(
        data,
        dict,
    ):

        return {
            "valid": False,
            "status": "INCONSISTENTE",
            "status_icon": "🔴",
            "message":
                "Os dados do Score não estão "
                "em formato válido.",
            "missing": [],
            "invalid": [],
        }

    validation = validate_indicators(
        data
    )

    return validation


# ==========================================================
# CONTRIBUIÇÃO DA MA21
# ==========================================================

def calculate_ma21_contribution(
    price,
    ma21,
):
    """
    Calcula a contribuição da MA21.

    Regra:

        Preço > MA21  -> +10
        Preço < MA21  -> -10
        Preço = MA21  ->  0
    """

    if not is_valid_number(
        price
    ) or not is_valid_number(
        ma21
    ):

        return {
            "points": 0,
            "signal": "Indisponível",
            "reason":
                "Dados insuficientes para avaliar a MA21.",
            "valid": False,
        }

    price = float(price)
    ma21 = float(ma21)

    if price > ma21:

        return {
            "points": 10,
            "signal": "Positivo",
            "reason":
                "Preço acima da MA21.",
            "valid": True,
        }

    if price < ma21:

        return {
            "points": -10,
            "signal": "Negativo",
            "reason":
                "Preço abaixo da MA21.",
            "valid": True,
        }

    return {
        "points": 0,
        "signal": "Neutro",
        "reason":
            "Preço alinhado à MA21.",
        "valid": True,
    }


# ==========================================================
# CONTRIBUIÇÃO DA MA200
# ==========================================================

def calculate_ma200_contribution(
    price,
    ma200,
):
    """
    Calcula a contribuição da MA200.

    Regra:

        Preço > MA200  -> +20
        Preço < MA200  -> -20
        Preço = MA200  ->  0
    """

    if not is_valid_number(
        price
    ) or not is_valid_number(
        ma200
    ):

        return {
            "points": 0,
            "signal": "Indisponível",
            "reason":
                "Dados insuficientes para avaliar a MA200.",
            "valid": False,
        }

    price = float(price)
    ma200 = float(ma200)

    if price > ma200:

        return {
            "points": 20,
            "signal": "Positivo",
            "reason":
                "Preço acima da MA200.",
            "valid": True,
        }

    if price < ma200:

        return {
            "points": -20,
            "signal": "Negativo",
            "reason":
                "Preço abaixo da MA200.",
            "valid": True,
        }

    return {
        "points": 0,
        "signal": "Neutro",
        "reason":
            "Preço alinhado à MA200.",
        "valid": True,
    }


# ==========================================================
# CONTRIBUIÇÃO DO RSI
# ==========================================================

def calculate_rsi_contribution(
    rsi,
):
    """
    Calcula a contribuição do RSI.

    Regra:

        RSI <= sobrevenda -> +10
        RSI >= sobrecompra -> -10
        Demais valores -> 0
    """

    if not is_valid_number(
        rsi
    ):

        return {
            "points": 0,
            "signal": "Indisponível",
            "reason":
                "Dados insuficientes para avaliar o RSI.",
            "valid": False,
        }

    rsi = float(rsi)

    # ------------------------------------------------------
    # Proteção adicional
    # ------------------------------------------------------

    if rsi < 0 or rsi > 100:

        return {
            "points": 0,
            "signal": "Inválido",
            "reason":
                "RSI fora do intervalo válido de 0 a 100.",
            "valid": False,
        }

    # ------------------------------------------------------
    # SOBREVENDA
    # ------------------------------------------------------

    if rsi <= RSI_OVERSOLD:

        return {
            "points": 10,
            "signal": "Positivo",
            "reason":
                "RSI em região de sobrevenda.",
            "valid": True,
        }

    # ------------------------------------------------------
    # SOBRECOMPRA
    # ------------------------------------------------------

    if rsi >= RSI_OVERBOUGHT:

        return {
            "points": -10,
            "signal": "Negativo",
            "reason":
                "RSI em região de sobrecompra.",
            "valid": True,
        }

    # ------------------------------------------------------
    # NEUTRO
    # ------------------------------------------------------

    return {
        "points": 0,
        "signal": "Neutro",
        "reason":
            "RSI em região neutra.",
        "valid": True,
    }


# ==========================================================
# CONTRIBUIÇÃO DA VOLATILIDADE
# ==========================================================

def validate_volatility_for_score(
    volatility,
):
    """
    A volatilidade não altera o Score nesta versão.

    Esta função existe para garantir que valores
    inválidos não sejam propagados para outras etapas.
    """

    if volatility is None:

        return {
            "valid": True,
            "available": False,
            "value": None,
        }

    value = safe_float(
        volatility
    )

    if value is None:

        return {
            "valid": False,
            "available": True,
            "value": None,
        }

    if value < 0:

        return {
            "valid": False,
            "available": True,
            "value": None,
        }

    return {
        "valid": True,
        "available": True,
        "value": value,
    }


# ==========================================================
# BREAKDOWN DO SCORE
# ==========================================================

def get_score_breakdown(
    data,
):
    """
    Calcula a contribuição individual
    de cada indicador para o Score.

    Score base:
        50 pontos

    MA21:
        +10 / -10

    MA200:
        +20 / -20

    RSI:
        +10 / -10 / 0

    IMPORTANTE:
        Se qualquer indicador obrigatório
        estiver inválido, o Score não é calculado.
    """

    # ======================================================
    # VALIDAÇÃO INICIAL
    # ======================================================

    validation = validate_score_data(
        data
    )

    if not validation["valid"]:

        return {

            "valid": False,

            "status":
                validation["status"],

            "status_icon":
                validation["status_icon"],

            "message":
                validation["message"],

            "missing":
                validation.get(
                    "missing",
                    [],
                ),

            "invalid":
                validation.get(
                    "invalid",
                    [],
                ),

            "base":
                50,

            "ma21": {
                "points": 0,
                "signal": "Indisponível",
                "reason":
                    "MA21 não pode ser utilizada.",
                "valid": False,
            },

            "ma200": {
                "points": 0,
                "signal": "Indisponível",
                "reason":
                    "MA200 não pode ser utilizada.",
                "valid": False,
            },

            "rsi": {
                "points": 0,
                "signal": "Indisponível",
                "reason":
                    "RSI não pode ser utilizado.",
                "valid": False,
            },

            "raw_score": None,

            "score": None,
        }

    # ======================================================
    # NORMALIZAÇÃO
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

    volatility = data.get(
        "volatility"
    )

    # ======================================================
    # SEGURANÇA
    # ======================================================

    if (
        price is None
        or ma21 is None
        or ma200 is None
        or rsi is None
    ):

        return {

            "valid": False,

            "status":
                "INCONSISTENTE",

            "status_icon":
                "🔴",

            "message":
                "Não foi possível converter "
                "os dados obrigatórios para números.",

            "missing": [],

            "invalid": [
                "price",
                "ma21",
                "ma200",
                "rsi",
            ],

            "base": 50,

            "ma21": {
                "points": 0,
                "signal": "Indisponível",
                "reason":
                    "Dados inválidos.",
                "valid": False,
            },

            "ma200": {
                "points": 0,
                "signal": "Indisponível",
                "reason":
                    "Dados inválidos.",
                "valid": False,
            },

            "rsi": {
                "points": 0,
                "signal": "Indisponível",
                "reason":
                    "Dados inválidos.",
                "valid": False,
            },

            "raw_score": None,

            "score": None,
        }

    # ======================================================
    # VALIDAÇÃO DA VOLATILIDADE
    # ======================================================

    volatility_validation = (
        validate_volatility_for_score(
            volatility
        )
    )

    # A volatilidade não invalida o Score,
    # pois não participa do cálculo nesta fase.

    # ======================================================
    # BASE
    # ======================================================

    base = 50

    # ======================================================
    # MA21
    # ======================================================

    ma21_result = calculate_ma21_contribution(
        price,
        ma21,
    )

    # ======================================================
    # MA200
    # ======================================================

    ma200_result = calculate_ma200_contribution(
        price,
        ma200,
    )

    # ======================================================
    # RSI
    # ======================================================

    rsi_result = calculate_rsi_contribution(
        rsi
    )

    # ======================================================
    # VERIFICAÇÃO FINAL DOS COMPONENTES
    # ======================================================

    components_valid = (
        ma21_result["valid"]
        and ma200_result["valid"]
        and rsi_result["valid"]
    )

    if not components_valid:

        return {

            "valid": False,

            "status":
                "INCONSISTENTE",

            "status_icon":
                "🔴",

            "message":
                "Um ou mais componentes "
                "do Score são inválidos.",

            "missing": [],

            "invalid": [
                "componentes",
            ],

            "base":
                base,

            "ma21":
                ma21_result,

            "ma200":
                ma200_result,

            "rsi":
                rsi_result,

            "volatility":
                volatility_validation,

            "raw_score":
                None,

            "score":
                None,
        }

    # ======================================================
    # SCORE BRUTO
    # ======================================================

    raw_score = (
        base
        + ma21_result["points"]
        + ma200_result["points"]
        + rsi_result["points"]
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

        "valid": True,

        "status":
            "CONSISTENTE",

        "status_icon":
            "🟢",

        "message":
            "Score calculado com dados válidos.",

        "missing": [],

        "invalid": [],

        "base":
            base,

        "ma21": {

            "points":
                ma21_result["points"],

            "signal":
                ma21_result["signal"],

            "reason":
                ma21_result["reason"],

            "valid":
                ma21_result["valid"],
        },

        "ma200": {

            "points":
                ma200_result["points"],

            "signal":
                ma200_result["signal"],

            "reason":
                ma200_result["reason"],

            "valid":
                ma200_result["valid"],
        },

        "rsi": {

            "points":
                rsi_result["points"],

            "signal":
                rsi_result["signal"],

            "reason":
                rsi_result["reason"],

            "valid":
                rsi_result["valid"],
        },

        "volatility":
            volatility_validation,

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
    Calcula o Score InvestIA de 0 a 100.

    Retorna None quando os dados não são suficientes.
    """

    breakdown = get_score_breakdown(
        data
    )

    return breakdown.get(
        "score"
    )


# ==========================================================
# CLASSIFICAÇÃO
# ==========================================================

def classify_score(
    score,
):
    """
    Classifica o Score InvestIA.

    Retorna INDISPONÍVEL quando o Score
    não pode ser calculado.
    """

    if not is_valid_number(
        score
    ):

        return "INDISPONÍVEL"

    score = clamp_score(
        score
    )

    if score is None:

        return "INDISPONÍVEL"

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

    Retorna INDISPONÍVEL quando não existe
    Score confiável.
    """

    if not is_valid_number(
        score
    ):

        return "INDISPONÍVEL"

    score = clamp_score(
        score
    )

    if score is None:

        return "INDISPONÍVEL"

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
    Retorna o nível qualitativo do sinal.
    """

    if not is_valid_number(
        score
    ):

        return "Indisponível"

    score = clamp_score(
        score
    )

    if score is None:

        return "Indisponível"

    if score >= 80:

        return "Muito forte"

    if score >= BUY_SCORE:

        return "Forte"

    if score >= 50:

        return "Aguardar"

    if score > SELL_SCORE:

        return "Atenção"

    return "Forte negativo"


# ==========================================================
# ÍCONE DO SINAL
# ==========================================================

def get_signal_icon(
    signal,
):
    """
    Retorna o ícone correspondente ao sinal.
    """

    if signal is None:

        return "⚪"

    signal = str(
        signal
    ).upper()

    if (
        "POSITIVO" in signal
        or "COMPRA" in signal
    ):

        return "🟢"

    if (
        "NEGATIVO" in signal
        or "VENDA" in signal
    ):

        return "🔴"

    if (
        "INDISPONÍVEL" in signal
        or "INDISPONIVEL" in signal
    ):

        return "⚪"

    return "🟡"


# ==========================================================
# SCORE COMPLETO
# ==========================================================

def calculate_score_details(
    data,
):
    """
    Retorna o Score completo com:

        score
        classificação
        sinal
        nível
        ícone
        breakdown
        validação
    """

    breakdown = get_score_breakdown(
        data
    )

    score = breakdown.get(
        "score"
    )

    classification = classify_score(
        score
    )

    signal = classify_signal(
        score
    )

    signal_level = get_signal_level(
        score
    )

    signal_icon = get_signal_icon(
        signal
    )

    return {

        "score":
            score,

        "classification":
            classification,

        "signal":
            signal,

        "signal_level":
            signal_level,

        "signal_icon":
            signal_icon,

        "breakdown":
            breakdown,

        "valid":
            breakdown.get(
                "valid",
                False,
            ),

        "status":
            breakdown.get(
                "status",
                "INCONSISTENTE",
            ),

        "status_icon":
            breakdown.get(
                "status_icon",
                "🔴",
            ),

        "message":
            breakdown.get(
                "message",
                "",
            ),

        "missing":
            breakdown.get(
                "missing",
                [],
            ),

        "invalid":
            breakdown.get(
                "invalid",
                [],
            ),
    }
