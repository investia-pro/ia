"""
InvestIA PRO
Motor de Análise e Inteligência de Sinais

Versão: v0.6
Fase: 2.8.1 - Motor de Sinais
"""

from score import (
    calculate_score_details,
)


# ==========================================================
# CONFIGURAÇÕES DO MOTOR DE SINAIS
# ==========================================================

RSI_OVERSOLD_DEFAULT = 30
RSI_OVERBOUGHT_DEFAULT = 70

STRONG_SIGNAL_SCORE = 80
BUY_SIGNAL_SCORE = 65
NEUTRAL_SCORE = 50
SELL_SIGNAL_SCORE = 35

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
    Converte um valor para texto com segurança.
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

    signal = str(signal).strip().upper()

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
    Valida os dados necessários para a análise.
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
            "reason": (
                "O preço está acima da MA21, "
                "indicando força de curto prazo."
            ),
        }

    if price < ma21:

        return {
            "signal": "NEGATIVO",
            "confirmation": True,
            "reason": (
                "O preço está abaixo da MA21, "
                "indicando fraqueza de curto prazo."
            ),
        }

    return {
        "signal": "NEUTRO",
        "confirmation": False,
        "reason": (
            "O preço está alinhado à MA21."
        ),
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
            "reason": (
                "O preço está acima da MA200, "
                "indicando tendência estrutural positiva."
            ),
        }

    if price < ma200:

        return {
            "signal": "NEGATIVO",
            "confirmation": True,
            "reason": (
                "O preço está abaixo da MA200, "
                "indicando tendência estrutural negativa."
            ),
        }

    return {
        "signal": "NEUTRO",
        "confirmation": False,
        "reason": (
            "O preço está alinhado à MA200."
        ),
    }


# ==========================================================
# ANÁLISE DO RSI
# ==========================================================

def analyze_rsi(rsi):
    """
    Analisa o RSI.

    RSI <= 30:
        sobrevenda / potencial recuperação

    RSI >= 70:
        sobrecompra / atenção à correção

    Entre 30 e 70:
        região neutra
    """

    if rsi <= RSI_OVERSOLD_DEFAULT:

        return {
            "signal": "POSITIVO",
            "confirmation": True,
            "status": "Sobrevenda",
            "reason": (
                "RSI em região de sobrevenda, "
                "podendo indicar oportunidade de recuperação."
            ),
        }

    if rsi >= RSI_OVERBOUGHT_DEFAULT:

        return {
            "signal": "NEGATIVO",
            "confirmation": True,
            "status": "Sobrecompra",
            "reason": (
                "RSI em região de sobrecompra, "
                "indicando atenção para possível correção."
            ),
        }

    return {
        "signal": "NEUTRO",
        "confirmation": False,
        "status": "Neutro",
        "reason": (
            "RSI em região neutra."
        ),
    }


# ==========================================================
# DETERMINAÇÃO DA TENDÊNCIA
# ==========================================================

def determine_trend(
    price,
    ma21,
    ma200,
):
    """
    Determina a tendência utilizando
    MA21 e MA200.
    """

    short_term_positive = price > ma21
    long_term_positive = price > ma200

    short_term_negative = price < ma21
    long_term_negative = price < ma200

    if (
        short_term_positive
        and long_term_positive
    ):

        return "Positiva"

    if (
        short_term_negative
        and long_term_negative
    ):

        return "Negativa"

    return "Neutra"


# ==========================================================
# CONTAGEM DE CONFIRMAÇÕES
# ==========================================================

def calculate_confirmations(
    ma21_analysis,
    ma200_analysis,
    rsi_analysis,
):
    """
    Conta confirmações positivas e negativas.
    """

    analyses = [
        ma21_analysis,
        ma200_analysis,
        rsi_analysis,
    ]

    positive = sum(
        1
        for item in analyses
        if item.get("signal") == "POSITIVO"
    )

    negative = sum(
        1
        for item in analyses
        if item.get("signal") == "NEGATIVO"
    )

    neutral = sum(
        1
        for item in analyses
        if item.get("signal") == "NEUTRO"
    )

    return {
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
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

    Forte:
        Score >= 80
        e pelo menos 2 confirmações.

    Moderado:
        Score >= 65
        ou pelo menos 2 confirmações.

    Fraco:
        sinal existente sem confirmação suficiente.

    Aguardar:
        sinal neutro.
    """

    if signal == "NEUTRO":

        return {
            "level": "Aguardar",
            "icon": "🟡",
            "description": (
                "Os indicadores não apresentam "
                "confirmação suficiente."
            ),
        }

    if (
        score >= STRONG_SIGNAL_SCORE
        and confirmations >= STRONG_CONFIRMATIONS
    ):

        return {
            "level": "Forte",
            "icon": "🟢",
            "description": (
                "Sinal confirmado por múltiplos "
                "indicadores."
            ),
        }

    if (
        score >= BUY_SIGNAL_SCORE
        and confirmations >= 1
    ):

        return {
            "level": "Moderado",
            "icon": "🟢",
            "description": (
                "Sinal favorável, porém com "
                "confirmação parcial."
            ),
        }

    if (
        score <= SELL_SIGNAL_SCORE
        and confirmations >= 1
    ):

        return {
            "level": "Moderado",
            "icon": "🔴",
            "description": (
                "Sinal desfavorável com "
                "confirmação parcial."
            ),
        }

    return {
        "level": "Fraco",
        "icon": "🟡",
        "description": (
            "Existe sinal, mas a confirmação "
            "técnica é limitada."
        ),
    }


# ==========================================================
# SINAL QUALIFICADO
# ==========================================================

def determine_qualified_signal(
    signal,
    strength_level,
):
    """
    Cria o sinal apresentado ao usuário.
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
# RECOMENDAÇÃO
# ==========================================================

def determine_recommendation(
    score,
    signal,
    strength_level,
    trend,
):
    """
    Define a recomendação operacional.
    """

    if (
        signal == "POSITIVO"
        and strength_level == "Forte"
        and trend == "Positiva"
    ):

        return "Compra"

    if (
        signal == "POSITIVO"
        and strength_level in [
            "Forte",
            "Moderado",
        ]
    ):

        return "Compra Moderada"

    if (
        signal == "NEGATIVO"
        and strength_level == "Forte"
        and trend == "Negativa"
    ):

        return "Venda"

    if (
        signal == "NEGATIVO"
        and strength_level in [
            "Forte",
            "Moderado",
        ]
    ):

        return "Venda Moderada"

    return "Aguardar"


# ==========================================================
# NÍVEL DE RISCO
# ==========================================================

def determine_risk(
    score,
    signal,
    trend,
    confirmations,
):
    """
    Determina o nível de risco da leitura.

    A análise é baseada em:
        - Score
        - Tendência
        - Confirmações
        - Divergências
    """

    if signal == "NEUTRO":

        return "Moderado"

    if (
        signal == "POSITIVO"
        and trend == "Positiva"
        and confirmations >= 2
        and score >= 80
    ):

        return "Baixo"

    if (
        signal == "NEGATIVO"
        and trend == "Negativa"
        and confirmations >= 2
        and score <= 20
    ):

        return "Alto"

    if (
        confirmations >= 2
        and (
            trend == "Positiva"
            or trend == "Negativa"
        )
    ):

        return "Moderado"

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
    risk,
    confirmations,
):
    """
    Gera o resumo executivo da análise.
    """

    asset = safe_text(
        asset,
        "Ativo",
    )

    if signal == "POSITIVO":

        if confirmations >= 2:

            return (
                f"{asset} apresenta cenário técnico "
                f"favorável, com Score InvestIA de "
                f"{score}/100 e confirmação positiva "
                f"por múltiplos indicadores. "
                f"Tendência {trend.lower()}, "
                f"sinal {qualified_signal.lower()} "
                f"e recomendação de {recommendation.lower()}. "
                f"Nível de risco: {risk.lower()}."
            )

        return (
            f"{asset} apresenta viés positivo, "
            f"com Score InvestIA de {score}/100. "
            f"O sinal ainda possui confirmação parcial. "
            f"Recomendação: {recommendation.lower()}."
        )

    if signal == "NEGATIVO":

        if confirmations >= 2:

            return (
                f"{asset} apresenta cenário técnico "
                f"desfavorável, com Score InvestIA de "
                f"{score}/100 e confirmação negativa "
                f"por múltiplos indicadores. "
                f"Tendência {trend.lower()}, "
                f"sinal {qualified_signal.lower()} "
                f"e recomendação de {recommendation.lower()}. "
                f"Nível de risco: {risk.lower()}."
            )

        return (
            f"{asset} apresenta viés negativo, "
            f"com Score InvestIA de {score}/100. "
            f"O sinal possui confirmação parcial. "
            f"Recomendação: {recommendation.lower()}."
        )

    return (
        f"{asset} apresenta cenário técnico "
        f"sem confirmação suficiente para uma "
        f"decisão direcional. Score InvestIA de "
        f"{score}/100, tendência {trend.lower()} "
        f"e recomendação de aguardar."
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

    Parâmetros:
        data:
            Dicionário contendo:
                price
                rsi
                ma21
                ma200
                volatility

        asset:
            Código do ativo.

    Retorno:
        Dicionário completo para o Dashboard.
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
    # SCORE INVESTIA
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
    # ANÁLISE DOS INDICADORES
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

    positive_confirmations = confirmation_data[
        "positive"
    ]

    negative_confirmations = confirmation_data[
        "negative"
    ]

    neutral_confirmations = confirmation_data[
        "neutral"
    ]

    # ======================================================
    # AJUSTE DO SINAL
    # ======================================================

    signal = base_signal

    # ------------------------------------------------------
    # Se o Score indica compra, mas existem indicadores
    # negativos relevantes, reduzimos a confiança.
    # ------------------------------------------------------

    if signal == "POSITIVO":

        if (
            negative_confirmations
            >= 2
        ):

            signal = "NEUTRO"

    # ------------------------------------------------------
    # Se o Score indica venda, mas existem indicadores
    # positivos relevantes, reduzimos a confiança.
    # ------------------------------------------------------

    elif signal == "NEGATIVO":

        if (
            positive_confirmations
            >= 2
        ):

            signal = "NEUTRO"

    # ======================================================
    # CONFIRMAÇÕES UTILIZADAS PELO SINAL
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
    # FORÇA
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
    # SINAL QUALIFICADO
    # ======================================================

    qualified_signal = determine_qualified_signal(
        signal,
        signal_level,
    )

    # ======================================================
    # RECOMENDAÇÃO
    # ======================================================

    recommendation = determine_recommendation(
        score,
        signal,
        signal_level,
        trend,
    )

    # ======================================================
    # RISCO
    # ======================================================

    risk = determine_risk(
        score,
        signal,
        trend,
        confirmations,
    )

    # ======================================================
    # STATUS DO RSI
    # ======================================================

    rsi_status = rsi_analysis.get(
        "status",
        "Neutro",
    )

    # ======================================================
    # JUSTIFICATIVAS
    # ======================================================

    reasons = []

    reasons.append(
        ma21_analysis["reason"]
    )

    reasons.append(
        ma200_analysis["reason"]
    )

    reasons.append(
        rsi_analysis["reason"]
    )

    # ------------------------------------------------------
    # Confirmação geral
    # ------------------------------------------------------

    if signal == "POSITIVO":

        reasons.append(
            f"{positive_confirmations} indicador(es) "
            f"apresentam sinal positivo."
        )

    elif signal == "NEGATIVO":

        reasons.append(
            f"{negative_confirmations} indicador(es) "
            f"apresentam sinal negativo."
        )

    else:

        reasons.append(
            "Os indicadores apresentam sinais "
            "sem confirmação direcional suficiente."
        )

    # ======================================================
    # RESUMO EXECUTIVO
    # ======================================================

    executive_summary = build_executive_summary(
        asset,
        score,
        trend,
        signal,
        qualified_signal,
        recommendation,
        risk,
        confirmations,
    )

    # ======================================================
    # RETORNO
    # ======================================================

    return {

        # --------------------------------------------------
        # IDENTIFICAÇÃO
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
        # RESUMO
        # --------------------------------------------------

        "executive_summary":
            executive_summary,

    }


# ==========================================================
# FUNÇÃO DE TESTE
# ==========================================================

def get_signal_summary(result):
    """
    Retorna somente os principais elementos do sinal.
    """

    if not isinstance(result, dict):
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

        "risk":
            result.get(
                "risk",
                "Moderado",
            ),

    }
