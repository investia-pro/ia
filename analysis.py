"""
InvestIA PRO
Motor de Análise e Recomendação Operacional

Versão: v0.6
Fase: 2.8.3 - Recomendação Operacional
"""

from score import (
    calculate_score_details,
)


# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

RSI_OVERSOLD_DEFAULT = 30
RSI_OVERBOUGHT_DEFAULT = 70

STRONG_SCORE = 80
BUY_SCORE = 65
NEUTRAL_SCORE = 50
SELL_SCORE = 35

STRONG_CONFIRMATIONS = 2


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def safe_float(value, default=None):
    """
    Converte um valor para float com segurança.
    """

    try:

        if value is None:
            return default

        return float(value)

    except (TypeError, ValueError):

        return default


def safe_text(value, default=""):
    """
    Converte um valor para texto.
    """

    if value is None:
        return default

    return str(value)


def normalize_signal(signal):
    """
    Normaliza diferentes formatos de sinal.
    """

    if signal is None:
        return "NEUTRO"

    signal = (
        str(signal)
        .strip()
        .upper()
    )

    mapping = {

        "POSITIVO": "POSITIVO",
        "POSITIVE": "POSITIVO",
        "COMPRA": "POSITIVO",
        "BUY": "POSITIVO",

        "NEGATIVO": "NEGATIVO",
        "NEGATIVE": "NEGATIVO",
        "VENDA": "NEGATIVO",
        "SELL": "NEGATIVO",

        "NEUTRO": "NEUTRO",
        "NEUTRAL": "NEUTRO",
        "AGUARDAR": "NEUTRO",
    }

    return mapping.get(
        signal,
        "NEUTRO",
    )


# ==========================================================
# VALIDAÇÃO
# ==========================================================

def validate_analysis_data(data):
    """
    Valida os campos necessários para análise.
    """

    if data is None:
        return False

    if not isinstance(data, dict):
        return False

    required = [
        "price",
        "rsi",
        "ma21",
        "ma200",
    ]

    for field in required:

        if field not in data:
            return False

        if data[field] is None:
            return False

        if safe_float(data[field]) is None:
            return False

    return True


# ==========================================================
# ANÁLISE DA MA21
# ==========================================================

def analyze_ma21(price, ma21):
    """
    Analisa a posição do preço em relação à MA21.
    """

    if price > ma21:

        return {

            "signal": "POSITIVO",

            "confirmation": True,

            "reason":
                "Preço acima da MA21, "
                "indicando força de curto prazo.",
        }

    if price < ma21:

        return {

            "signal": "NEGATIVO",

            "confirmation": True,

            "reason":
                "Preço abaixo da MA21, "
                "indicando fraqueza de curto prazo.",
        }

    return {

        "signal": "NEUTRO",

        "confirmation": False,

        "reason":
            "Preço alinhado à MA21.",
    }


# ==========================================================
# ANÁLISE DA MA200
# ==========================================================

def analyze_ma200(price, ma200):
    """
    Analisa a posição do preço em relação à MA200.
    """

    if price > ma200:

        return {

            "signal": "POSITIVO",

            "confirmation": True,

            "reason":
                "Preço acima da MA200, "
                "indicando tendência estrutural positiva.",
        }

    if price < ma200:

        return {

            "signal": "NEGATIVO",

            "confirmation": True,

            "reason":
                "Preço abaixo da MA200, "
                "indicando tendência estrutural negativa.",
        }

    return {

        "signal": "NEUTRO",

        "confirmation": False,

        "reason":
            "Preço alinhado à MA200.",
    }


# ==========================================================
# ANÁLISE DO RSI
# ==========================================================

def analyze_rsi(rsi):
    """
    Analisa o RSI.
    """

    if rsi <= RSI_OVERSOLD_DEFAULT:

        return {

            "signal": "POSITIVO",

            "confirmation": True,

            "status": "Sobrevenda",

            "reason":
                "RSI em região de sobrevenda, "
                "podendo indicar recuperação.",
        }

    if rsi >= RSI_OVERBOUGHT_DEFAULT:

        return {

            "signal": "NEGATIVO",

            "confirmation": True,

            "status": "Sobrecompra",

            "reason":
                "RSI em região de sobrecompra, "
                "indicando atenção para possível correção.",
        }

    return {

        "signal": "NEUTRO",

        "confirmation": False,

        "status": "Neutro",

        "reason":
            "RSI em região neutra.",
    }


# ==========================================================
# TENDÊNCIA
# ==========================================================

def determine_trend(
    price,
    ma21,
    ma200,
):
    """
    Determina a tendência utilizando MA21 e MA200.
    """

    if (
        price > ma21
        and price > ma200
    ):

        return "Positiva"

    if (
        price < ma21
        and price < ma200
    ):

        return "Negativa"

    return "Neutra"


# ==========================================================
# CONFIRMAÇÕES
# ==========================================================

def calculate_confirmations(
    ma21_analysis,
    ma200_analysis,
    rsi_analysis,
):
    """
    Conta sinais positivos, negativos e neutros.
    """

    analyses = [

        ma21_analysis,
        ma200_analysis,
        rsi_analysis,

    ]

    positive = sum(

        1

        for item in analyses

        if item.get("signal")
        == "POSITIVO"

    )

    negative = sum(

        1

        for item in analyses

        if item.get("signal")
        == "NEGATIVO"

    )

    neutral = sum(

        1

        for item in analyses

        if item.get("signal")
        == "NEUTRO"

    )

    return {

        "positive":
            positive,

        "negative":
            negative,

        "neutral":
            neutral,

    }


# ==========================================================
# FORÇA DO SINAL
# ==========================================================

def determine_signal_strength(
    score,
    confirmations,
    signal,
):
    """
    Determina a força do sinal.
    """

    if signal == "NEUTRO":

        return {

            "level":
                "Aguardar",

            "icon":
                "🟡",

            "description":
                "Indicadores sem confirmação "
                "direcional suficiente.",
        }

    if (
        score >= STRONG_SCORE
        and confirmations >= STRONG_CONFIRMATIONS
    ):

        return {

            "level":
                "Forte",

            "icon":
                "🟢",

            "description":
                "Sinal confirmado por múltiplos "
                "indicadores.",
        }

    if (
        score >= BUY_SCORE
        and confirmations >= 1
    ):

        return {

            "level":
                "Moderado",

            "icon":
                "🟢",

            "description":
                "Sinal favorável com confirmação "
                "técnica parcial.",
        }

    if (
        score <= SELL_SCORE
        and confirmations >= 1
    ):

        return {

            "level":
                "Moderado",

            "icon":
                "🔴",

            "description":
                "Sinal desfavorável com confirmação "
                "técnica parcial.",
        }

    return {

        "level":
            "Fraco",

        "icon":
            "🟡",

        "description":
            "Existe sinal, mas a confirmação "
            "técnica é limitada.",
    }


# ==========================================================
# CONFIANÇA
# ==========================================================

def calculate_confidence(
    score,
    signal,
    confirmations,
    contradictions,
    trend,
):
    """
    Calcula a confiança interna do modelo.

    A confiança representa a consistência
    dos indicadores disponíveis.

    Não representa probabilidade de retorno.
    """

    confidence = 50

    # ------------------------------------------------------
    # SCORE
    # ------------------------------------------------------

    if (
        score >= 80
        or score <= 20
    ):

        confidence += 20

    elif (
        score >= 65
        or score <= 35
    ):

        confidence += 10

    # ------------------------------------------------------
    # CONFIRMAÇÕES
    # ------------------------------------------------------

    confidence += (
        confirmations * 10
    )

    # ------------------------------------------------------
    # CONTRADIÇÕES
    # ------------------------------------------------------

    confidence -= (
        contradictions * 15
    )

    # ------------------------------------------------------
    # TENDÊNCIA
    # ------------------------------------------------------

    if signal == "POSITIVO":

        if trend == "Positiva":
            confidence += 10

        elif trend == "Negativa":
            confidence -= 10

    elif signal == "NEGATIVO":

        if trend == "Negativa":
            confidence += 10

        elif trend == "Positiva":
            confidence -= 10

    # ------------------------------------------------------
    # LIMITAÇÃO
    # ------------------------------------------------------

    confidence = max(
        0,
        min(
            100,
            int(round(confidence)),
        ),
    )

    # ------------------------------------------------------
    # CLASSIFICAÇÃO
    # ------------------------------------------------------

    if confidence >= 80:

        label = "Alta"

    elif confidence >= 60:

        label = "Moderada"

    else:

        label = "Baixa"

    return {

        "value":
            confidence,

        "label":
            label,

    }


# ==========================================================
# SINAL QUALIFICADO
# ==========================================================

def determine_qualified_signal(
    signal,
    strength_level,
):
    """
    Define o sinal qualificado.
    """

    if signal == "POSITIVO":

        if strength_level == "Forte":
            return "COMPRA FORTE"

        if strength_level == "Moderado":
            return "COMPRA"

        return "COMPRA FRACA"

    if signal == "NEGATIVO":

        if strength_level == "Forte":
            return "VENDA FORTE"

        if strength_level == "Moderado":
            return "VENDA"

        return "VENDA FRACA"

    return "AGUARDAR"


# ==========================================================
# RECOMENDAÇÃO OPERACIONAL
# ==========================================================

def determine_operational_recommendation(
    score,
    signal,
    strength_level,
    confidence_label,
    trend,
    confirmations,
    contradictions,
):
    """
    Converte o sinal técnico em recomendação operacional.

    A recomendação é deliberadamente mais conservadora
    que o sinal.
    """

    # ======================================================
    # CENÁRIO POSITIVO
    # ======================================================

    if signal == "POSITIVO":

        # ----------------------------------------------
        # COMPRA FORTE
        # ----------------------------------------------

        if (
            strength_level == "Forte"
            and confidence_label == "Alta"
            and trend == "Positiva"
            and confirmations >= 2
            and contradictions == 0
        ):

            return {

                "recommendation":
                    "Compra",

                "action":
                    "Entrada favorável",

                "icon":
                    "🟢",

                "reason":
                    "Cenário positivo confirmado "
                    "por múltiplos indicadores.",
            }

        # ----------------------------------------------
        # COMPRA MODERADA
        # ----------------------------------------------

        if (
            strength_level in [
                "Forte",
                "Moderado",
            ]
            and confidence_label in [
                "Alta",
                "Moderada",
            ]
            and confirmations >= 1
        ):

            return {

                "recommendation":
                    "Compra Moderada",

                "action":
                    "Entrada com cautela",

                "icon":
                    "🟢",

                "reason":
                    "Cenário favorável, porém "
                    "com confirmação parcial.",
            }

        # ----------------------------------------------
        # COMPRA FRACA
        # ----------------------------------------------

        return {

            "recommendation":
                "Aguardar Confirmação",

            "action":
                "Não antecipar entrada",

            "icon":
                "🟡",

            "reason":
                "O viés é positivo, mas a "
                "confirmação ainda é insuficiente.",
        }

    # ======================================================
    # CENÁRIO NEGATIVO
    # ======================================================

    if signal == "NEGATIVO":

        # ----------------------------------------------
        # VENDA FORTE
        # ----------------------------------------------

        if (
            strength_level == "Forte"
            and confidence_label == "Alta"
            and trend == "Negativa"
            and confirmations >= 2
            and contradictions == 0
        ):

            return {

                "recommendation":
                    "Venda",

                "action":
                    "Redução de exposição",

                "icon":
                    "🔴",

                "reason":
                    "Cenário negativo confirmado "
                    "por múltiplos indicadores.",
            }

        # ----------------------------------------------
        # VENDA MODERADA
        # ----------------------------------------------

        if (
            strength_level in [
                "Forte",
                "Moderado",
            ]
            and confidence_label in [
                "Alta",
                "Moderada",
            ]
            and confirmations >= 1
        ):

            return {

                "recommendation":
                    "Reduzir Exposição",

                "action":
                    "Reduzir risco",

                "icon":
                    "🔴",

                "reason":
                    "Cenário desfavorável com "
                    "confirmação parcial.",
            }

        # ----------------------------------------------
        # VENDA FRACA
        # ----------------------------------------------

        return {

            "recommendation":
                "Aguardar Confirmação",

            "action":
                "Evitar decisão precipitada",

            "icon":
                "🟡",

            "reason":
                "O viés é negativo, mas a "
                "confirmação ainda é insuficiente.",
        }

    # ======================================================
    # CENÁRIO NEUTRO
    # ======================================================

    return {

        "recommendation":
            "Aguardar",

        "action":
            "Sem ação",

        "icon":
            "🟡",

        "reason":
            "Os indicadores não apresentam "
            "direção suficientemente clara.",
    }


# ==========================================================
# RISCO
# ==========================================================

def determine_risk(
    score,
    signal,
    trend,
    confirmations,
    contradictions,
):
    """
    Determina o nível de risco da leitura.
    """

    if signal == "NEUTRO":

        return "Moderado"

    if (
        signal == "POSITIVO"
        and trend == "Positiva"
        and confirmations >= 2
        and contradictions == 0
        and score >= 80
    ):

        return "Baixo"

    if (
        signal == "NEGATIVO"
        and trend == "Negativa"
        and confirmations >= 2
        and contradictions == 0
        and score <= 20
    ):

        return "Alto"

    return "Moderado"


# ==========================================================
# RESUMO EXECUTIVO
# ==========================================================

def build_executive_summary(
    asset,
    score,
    trend,
    signal,
    qualified_signal,
    recommendation,
    confidence_label,
    risk,
):
    """
    Gera o resumo executivo.
    """

    asset = safe_text(
        asset,
        "Ativo",
    )

    if signal == "POSITIVO":

        return (
            f"{asset} apresenta viés técnico positivo, "
            f"com Score InvestIA de {score}/100 e "
            f"tendência {trend.lower()}. "
            f"O sinal é {qualified_signal.lower()}, "
            f"com confiança {confidence_label.lower()}. "
            f"Recomendação operacional: "
            f"{recommendation.lower()}. "
            f"Nível de risco: {risk.lower()}."
        )

    if signal == "NEGATIVO":

        return (
            f"{asset} apresenta viés técnico negativo, "
            f"com Score InvestIA de {score}/100 e "
            f"tendência {trend.lower()}. "
            f"O sinal é {qualified_signal.lower()}, "
            f"com confiança {confidence_label.lower()}. "
            f"Recomendação operacional: "
            f"{recommendation.lower()}. "
            f"Nível de risco: {risk.lower()}."
        )

    return (
        f"{asset} apresenta cenário técnico neutro, "
        f"com Score InvestIA de {score}/100 e "
        f"tendência {trend.lower()}. "
        f"Não há confirmação suficiente para uma "
        f"decisão direcional. "
        f"Recomendação operacional: "
        f"{recommendation.lower()}."
    )


# ==========================================================
# ANÁLISE PRINCIPAL
# ==========================================================

def analyze_asset(
    data,
    asset=None,
):
    """
    Executa a análise completa do ativo.
    """

    # ======================================================
    # VALIDAÇÃO
    # ======================================================

    if not validate_analysis_data(data):

        raise ValueError(
            "Dados insuficientes para realizar a análise."
        )

    # ======================================================
    # DADOS
    # ======================================================

    price = safe_float(
        data.get("price")
    )

    rsi = safe_float(
        data.get("rsi")
    )

    ma21 = safe_float(
        data.get("ma21")
    )

    ma200 = safe_float(
        data.get("ma200")
    )

    volatility = safe_float(
        data.get("volatility"),
        0,
    )

    # ======================================================
    # SCORE
    # ======================================================

    score_details = calculate_score_details(
        {
            "price": price,
            "ma21": ma21,
            "ma200": ma200,
            "rsi": rsi,
        }
    )

    score = score_details.get(
        "score",
        0,
    )

    classification = score_details.get(
        "classification",
        "NEUTRO",
    )

    base_signal = normalize_signal(
        score_details.get(
            "signal",
            "NEUTRO",
        )
    )

    breakdown = score_details.get(
        "breakdown",
        {},
    )

    # ======================================================
    # INDICADORES
    # ======================================================

    ma21_analysis = analyze_ma21(
        price,
        ma21,
    )

    ma200_analysis = analyze_ma200(
        price,
        ma200,
    )

    rsi_analysis = analyze_rsi(
        rsi,
    )

    # ======================================================
    # TENDÊNCIA
    # ======================================================

    trend = determine_trend(
        price,
        ma21,
        ma200,
    )

    # ======================================================
    # CONFIRMAÇÕES
    # ======================================================

    confirmation_data = calculate_confirmations(
        ma21_analysis,
        ma200_analysis,
        rsi_analysis,
    )

    positive_confirmations = (
        confirmation_data["positive"]
    )

    negative_confirmations = (
        confirmation_data["negative"]
    )

    neutral_confirmations = (
        confirmation_data["neutral"]
    )

    # ======================================================
    # CONTRADIÇÕES
    # ======================================================

    if base_signal == "POSITIVO":

        contradictions = (
            negative_confirmations
        )

    elif base_signal == "NEGATIVO":

        contradictions = (
            positive_confirmations
        )

    else:

        contradictions = 0

    # ======================================================
    # SINAL BASE
    # ======================================================

    signal = base_signal

    # ------------------------------------------------------
    # Duas ou mais contradições anulam o sinal.
    # ------------------------------------------------------

    if contradictions >= 2:

        signal = "NEUTRO"

    # ======================================================
    # CONFIRMAÇÕES DO SINAL
    # ======================================================

    if signal == "POSITIVO":

        confirmations = (
            positive_confirmations
        )

    elif signal == "NEGATIVO":

        confirmations = (
            negative_confirmations
        )

    else:

        confirmations = max(
            positive_confirmations,
            negative_confirmations,
        )

    # ======================================================
    # FORÇA DO SINAL
    # ======================================================

    strength = determine_signal_strength(
        score,
        confirmations,
        signal,
    )

    signal_level = strength[
        "level"
    ]

    signal_icon = strength[
        "icon"
    ]

    # ======================================================
    # CONFIANÇA
    # ======================================================

    confidence = calculate_confidence(
        score,
        signal,
        confirmations,
        contradictions,
        trend,
    )

    confidence_value = confidence[
        "value"
    ]

    confidence_label = confidence[
        "label"
    ]

    # ======================================================
    # SINAL QUALIFICADO
    # ======================================================

    qualified_signal = determine_qualified_signal(
        signal,
        signal_level,
    )

    # ======================================================
    # RECOMENDAÇÃO OPERACIONAL
    # ======================================================

    operational = (
        determine_operational_recommendation(
            score,
            signal,
            signal_level,
            confidence_label,
            trend,
            confirmations,
            contradictions,
        )
    )

    recommendation = operational[
        "recommendation"
    ]

    action = operational[
        "action"
    ]

    recommendation_icon = operational[
        "icon"
    ]

    recommendation_reason = operational[
        "reason"
    ]

    # ======================================================
    # RISCO
    # ======================================================

    risk = determine_risk(
        score,
        signal,
        trend,
        confirmations,
        contradictions,
    )

    # ======================================================
    # RSI
    # ======================================================

    rsi_status = rsi_analysis.get(
        "status",
        "Neutro",
    )

    # ======================================================
    # JUSTIFICATIVAS
    # ======================================================

    reasons = [

        ma21_analysis[
            "reason"
        ],

        ma200_analysis[
            "reason"
        ],

        rsi_analysis[
            "reason"
        ],

    ]

    # ------------------------------------------------------
    # CONFIRMAÇÃO
    # ------------------------------------------------------

    if signal == "POSITIVO":

        reasons.append(
            f"{positive_confirmations} indicador(es) "
            f"apresentam confirmação positiva."
        )

    elif signal == "NEGATIVO":

        reasons.append(
            f"{negative_confirmations} indicador(es) "
            f"apresentam confirmação negativa."
        )

    else:

        reasons.append(
            "Não existe confirmação direcional "
            "suficiente para uma entrada."
        )

    # ------------------------------------------------------
    # CONTRADIÇÕES
    # ------------------------------------------------------

    if contradictions > 0:

        reasons.append(
            f"Foram identificada(s) "
            f"{contradictions} contradição(ões) "
            f"em relação ao sinal principal."
        )

    # ======================================================
    # RESUMO EXECUTIVO
    # ======================================================

    executive_summary = (
        build_executive_summary(
            asset,
            score,
            trend,
            signal,
            qualified_signal,
            recommendation,
            confidence_label,
            risk,
        )
    )

    # ======================================================
    # RETORNO
    # ======================================================

    return {

        # --------------------------------------------------
        # ATIVO
        # --------------------------------------------------

        "asset":
            asset,

        # --------------------------------------------------
        # SCORE
        # --------------------------------------------------

        "score":
            score,

        "classification":
            classification,

        # --------------------------------------------------
        # SINAL
        # --------------------------------------------------

        "signal":
            signal,

        "qualified_signal":
            qualified_signal,

        "signal_level":
            signal_level,

        "signal_icon":
            signal_icon,

        # --------------------------------------------------
        # CONFIANÇA
        # --------------------------------------------------

        "confidence":
            confidence_value,

        "confidence_value":
            confidence_value,

        "confidence_label":
            confidence_label,

        # --------------------------------------------------
        # TENDÊNCIA
        # --------------------------------------------------

        "trend":
            trend,

        "tendencia":
            trend,

        # --------------------------------------------------
        # RECOMENDAÇÃO
        # --------------------------------------------------

        "recommendation":
            recommendation,

        "recomendacao":
            recommendation,

        "recommendation_icon":
            recommendation_icon,

        "recommendation_action":
            action,

        "recommendation_reason":
            recommendation_reason,

        # --------------------------------------------------
        # RISCO
        # --------------------------------------------------

        "risk":
            risk,

        "risco":
            risk,

        # --------------------------------------------------
        # RSI
        # --------------------------------------------------

        "rsi_status":
            rsi_status,

        # --------------------------------------------------
        # CONFIRMAÇÕES
        # --------------------------------------------------

        "confirmations":
            confirmations,

        "positive_confirmations":
            positive_confirmations,

        "negative_confirmations":
            negative_confirmations,

        "neutral_confirmations":
            neutral_confirmations,

        "contradictions":
            contradictions,

        # --------------------------------------------------
        # INDICADORES
        # --------------------------------------------------

        "indicator_analysis": {

            "ma21":
                ma21_analysis,

            "ma200":
                ma200_analysis,

            "rsi":
                rsi_analysis,

        },

        # --------------------------------------------------
        # VOLATILIDADE
        # --------------------------------------------------

        "volatility":
            volatility,

        # --------------------------------------------------
        # JUSTIFICATIVAS
        # --------------------------------------------------

        "reasons":
            reasons,

        "justificativas":
            reasons,

        # --------------------------------------------------
        # BREAKDOWN
        # --------------------------------------------------

        "breakdown":
            breakdown,

        # --------------------------------------------------
        # RESUMO EXECUTIVO
        # --------------------------------------------------

        "executive_summary":
            executive_summary,

    }


# ==========================================================
# RESUMO DO SINAL
# ==========================================================

def get_signal_summary(result):
    """
    Retorna somente os principais dados do sinal.
    """

    if not isinstance(
        result,
        dict,
    ):

        return {}

    return {

        "score":
            result.get(
                "score",
                0,
            ),

        "classification":
            result.get(
                "classification",
                "NEUTRO",
            ),

        "signal":
            result.get(
                "signal",
                "NEUTRO",
            ),

        "qualified_signal":
            result.get(
                "qualified_signal",
                "AGUARDAR",
            ),

        "signal_level":
            result.get(
                "signal_level",
                "Aguardar",
            ),

        "confidence":
            result.get(
                "confidence",
                0,
            ),

        "confidence_label":
            result.get(
                "confidence_label",
                "Baixa",
            ),

        "trend":
            result.get(
                "trend",
                "Neutra",
            ),

        "recommendation":
            result.get(
                "recommendation",
                "Aguardar",
            ),

        "recommendation_action":
            result.get(
                "recommendation_action",
                "Sem ação",
            ),

        "risk":
            result.get(
                "risk",
                "Moderado",
            ),

    }
