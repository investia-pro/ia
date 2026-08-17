"""
InvestIA PRO
Motor de Análise

Versão: v0.6
Fase: 2.8.4 - Consolidação do Dashboard Executivo
"""

from score import (
    calculate_score_details,
)


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def _safe_float(value, default=None):
    """
    Converte um valor para float com segurança.
    """

    try:

        if value is None:
            return default

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return default


def _safe_text(value, default=""):
    """
    Converte um valor para texto com segurança.
    """

    if value is None:
        return default

    return str(value)


def _get_breakdown_value(
    breakdown,
    indicator,
    key,
    default=None,
):
    """
    Obtém informações do breakdown do Score.
    """

    if not isinstance(
        breakdown,
        dict,
    ):
        return default

    data = breakdown.get(
        indicator,
        {},
    )

    if not isinstance(
        data,
        dict,
    ):
        return default

    return data.get(
        key,
        default,
    )


# ==========================================================
# TENDÊNCIA
# ==========================================================

def determine_trend(
    price,
    ma21,
    ma200,
):
    """
    Determina a tendência principal do ativo.

    Critérios:

    Positiva:
        preço acima da MA21 e MA200

    Negativa:
        preço abaixo da MA21 e MA200

    Mista:
        sinais divergentes
    """

    price = _safe_float(price)
    ma21 = _safe_float(ma21)
    ma200 = _safe_float(ma200)

    if (
        price is None
        or ma21 is None
        or ma200 is None
    ):

        return "Neutra"

    above_ma21 = price > ma21
    above_ma200 = price > ma200

    below_ma21 = price < ma21
    below_ma200 = price < ma200

    if above_ma21 and above_ma200:

        return "Positiva"

    if below_ma21 and below_ma200:

        return "Negativa"

    if (
        above_ma21
        and below_ma200
    ):

        return "Mista"

    if (
        below_ma21
        and above_ma200
    ):

        return "Mista"

    return "Neutra"


# ==========================================================
# STATUS DO RSI
# ==========================================================

def determine_rsi_status(rsi):
    """
    Classifica o RSI.

    <= 30:
        Sobrevenda

    >= 70:
        Sobrecompra

    30-70:
        Neutro
    """

    rsi = _safe_float(rsi)

    if rsi is None:

        return "Indisponível"

    if rsi <= 30:

        return "Sobrevenda"

    if rsi >= 70:

        return "Sobrecompra"

    return "Neutro"


# ==========================================================
# NÍVEL DO SINAL
# ==========================================================

def determine_signal_level(score):
    """
    Determina a força do sinal.
    """

    score = _safe_float(
        score,
        50,
    )

    if score >= 80:

        return "Forte"

    if score >= 65:

        return "Moderado"

    if score >= 50:

        return "Aguardar"

    if score >= 35:

        return "Moderado"

    return "Forte"


# ==========================================================
# ÍCONE DO SINAL
# ==========================================================

def determine_signal_icon(score):
    """
    Define o ícone visual do sinal.
    """

    score = _safe_float(
        score,
        50,
    )

    if score >= 65:

        return "🟢"

    if score <= 35:

        return "🔴"

    return "🟡"


# ==========================================================
# SINAL QUALIFICADO
# ==========================================================

def determine_qualified_signal(
    score,
    trend,
):
    """
    Gera o sinal operacional consolidado.

    O Score continua sendo o principal
    componente da decisão.

    A tendência é utilizada como
    confirmação contextual.
    """

    score = _safe_float(
        score,
        50,
    )

    trend = _safe_text(
        trend,
        "Neutra",
    )

    if score >= 80:

        return "COMPRA"

    if score >= 65:

        if trend == "Negativa":

            return "COMPRA COM CAUTELA"

        return "COMPRA"

    if score <= 35:

        return "VENDA"

    if score < 50:

        return "VENDA COM CAUTELA"

    return "AGUARDAR"


# ==========================================================
# RECOMENDAÇÃO
# ==========================================================

def determine_recommendation(
    score,
    trend,
    volatility,
):
    """
    Gera a recomendação final.

    O score define a direção principal.
    Tendência e volatilidade servem como
    filtros de contexto.
    """

    score = _safe_float(
        score,
        50,
    )

    volatility = _safe_float(
        volatility,
        0,
    )

    trend = _safe_text(
        trend,
        "Neutra",
    )

    # ------------------------------------------------------
    # Score muito forte
    # ------------------------------------------------------

    if score >= 80:

        if volatility >= 0.04:

            return "Compra com cautela"

        return "Compra"

    # ------------------------------------------------------
    # Score positivo
    # ------------------------------------------------------

    if score >= 65:

        if trend == "Negativa":

            return "Aguardar confirmação"

        if volatility >= 0.04:

            return "Compra com cautela"

        return "Compra"

    # ------------------------------------------------------
    # Score negativo
    # ------------------------------------------------------

    if score <= 35:

        return "Venda"

    # ------------------------------------------------------
    # Zona intermediária
    # ------------------------------------------------------

    if score < 50:

        return "Venda com cautela"

    return "Aguardar"


# ==========================================================
# GESTÃO DE RISCO
# ==========================================================

def determine_risk(
    volatility,
    score,
    trend,
):
    """
    Classifica o risco operacional.

    Volatilidade:
        < 2%   = Baixo
        < 4%   = Moderado
        >= 4%  = Alto

    Divergência entre Score e tendência
    pode elevar o risco.
    """

    volatility = _safe_float(
        volatility,
        0,
    )

    score = _safe_float(
        score,
        50,
    )

    trend = _safe_text(
        trend,
        "Neutra",
    )

    # ------------------------------------------------------
    # Volatilidade
    # ------------------------------------------------------

    if volatility >= 0.04:

        risk = "Alto"

    elif volatility >= 0.02:

        risk = "Moderado"

    else:

        risk = "Baixo"

    # ------------------------------------------------------
    # Divergência
    # ------------------------------------------------------

    divergence = (

        (
            score >= 65
            and trend == "Negativa"
        )

        or

        (
            score <= 35
            and trend == "Positiva"
        )

    )

    if divergence:

        if risk == "Baixo":

            risk = "Moderado"

        elif risk == "Moderado":

            risk = "Alto"

    return risk


# ==========================================================
# JUSTIFICATIVAS
# ==========================================================

def build_reasons(
    price,
    ma21,
    ma200,
    rsi,
    trend,
    risk,
):
    """
    Gera as justificativas utilizadas
    na seção de análise detalhada.
    """

    reasons = []

    price = _safe_float(price)
    ma21 = _safe_float(ma21)
    ma200 = _safe_float(ma200)
    rsi = _safe_float(rsi)

    # ------------------------------------------------------
    # MA21
    # ------------------------------------------------------

    if (
        price is not None
        and ma21 is not None
    ):

        if price > ma21:

            reasons.append(
                "O preço está acima da MA21, "
                "indicando força de curto prazo."
            )

        elif price < ma21:

            reasons.append(
                "O preço está abaixo da MA21, "
                "indicando pressão no curto prazo."
            )

        else:

            reasons.append(
                "O preço está alinhado à MA21."
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
                "O preço está acima da MA200, "
                "favorecendo a tendência de longo prazo."
            )

        elif price < ma200:

            reasons.append(
                "O preço está abaixo da MA200, "
                "indicando fraqueza em relação à tendência "
                "de longo prazo."
            )

        else:

            reasons.append(
                "O preço está alinhado à MA200."
            )

    # ------------------------------------------------------
    # RSI
    # ------------------------------------------------------

    if rsi is not None:

        if rsi <= 30:

            reasons.append(
                f"RSI em {rsi:.2f}, "
                "indicando região de sobrevenda."
            )

        elif rsi >= 70:

            reasons.append(
                f"RSI em {rsi:.2f}, "
                "indicando região de sobrecompra."
            )

        else:

            reasons.append(
                f"RSI em {rsi:.2f}, "
                "permanecendo em região neutra."
            )

    # ------------------------------------------------------
    # TENDÊNCIA
    # ------------------------------------------------------

    reasons.append(
        f"Tendência técnica identificada: {trend}."
    )

    # ------------------------------------------------------
    # RISCO
    # ------------------------------------------------------

    reasons.append(
        f"Nível de risco operacional: {risk}."
    )

    return reasons


# ==========================================================
# RESUMO EXECUTIVO
# ==========================================================

def build_executive_summary(
    asset,
    price,
    score,
    trend,
    risk,
    qualified_signal,
    recommendation,
    rsi,
):
    """
    Constrói o resumo executivo apresentado
    no Dashboard.
    """

    asset = _safe_text(
        asset,
        "Ativo",
    )

    price = _safe_float(
        price,
        0,
    )

    score = _safe_float(
        score,
        50,
    )

    rsi = _safe_float(
        rsi,
    )

    if rsi is None:

        rsi_text = "indisponível"

    else:

        rsi_text = f"{rsi:.2f}"

    return (
        f"{asset} apresenta Score InvestIA de "
        f"{int(round(score))}/100, com tendência "
        f"{trend.lower()} e sinal {qualified_signal}. "
        f"A recomendação atual é {recommendation.lower()}, "
        f"considerando risco {risk.lower()}. "
        f"O preço analisado é de R$ {price:,.2f} "
        f"e o RSI está em {rsi_text}."
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

    Entrada esperada:

    {
        "price": float,
        "rsi": float,
        "ma21": float,
        "ma200": float,
        "volatility": float
    }

    Retorno compatível com o app.py:
    
        score
        classification
        signal
        qualified_signal
        signal_level
        signal_icon
        trend
        recommendation
        risk
        rsi_status
        reasons
        breakdown
        executive_summary
    """

    # ======================================================
    # VALIDAÇÃO
    # ======================================================

    if data is None:

        raise ValueError(
            "Dados não fornecidos para análise."
        )

    if not isinstance(
        data,
        dict,
    ):

        raise TypeError(
            "Os dados da análise devem ser "
            "fornecidos como dicionário."
        )

    required = [
        "price",
        "rsi",
        "ma21",
        "ma200",
    ]

    missing = []

    for field in required:

        value = data.get(
            field
        )

        if value is None:

            missing.append(
                field
            )

    if missing:

        raise ValueError(
            "Dados insuficientes para análise: "
            + ", ".join(missing)
        )

    # ======================================================
    # NORMALIZAÇÃO
    # ======================================================

    price = _safe_float(
        data.get("price")
    )

    rsi = _safe_float(
        data.get("rsi")
    )

    ma21 = _safe_float(
        data.get("ma21")
    )

    ma200 = _safe_float(
        data.get("ma200")
    )

    volatility = _safe_float(
        data.get("volatility"),
        0,
    )

    if (
        price is None
        or rsi is None
        or ma21 is None
        or ma200 is None
    ):

        raise ValueError(
            "Um ou mais indicadores possuem "
            "valores inválidos."
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
        50,
    )

    classification = score_details.get(
        "classification",
        "NEUTRO",
    )

    signal = score_details.get(
        "signal",
        "NEUTRO",
    )

    breakdown = score_details.get(
        "breakdown",
        {},
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
    # RSI
    # ======================================================

    rsi_status = determine_rsi_status(
        rsi
    )

    # ======================================================
    # SINAL QUALIFICADO
    # ======================================================

    qualified_signal = determine_qualified_signal(
        score,
        trend,
    )

    # ======================================================
    # NÍVEL DO SINAL
    # ======================================================

    signal_level = determine_signal_level(
        score
    )

    signal_icon = determine_signal_icon(
        score
    )

    # ======================================================
    # RECOMENDAÇÃO
    # ======================================================

    recommendation = determine_recommendation(
        score,
        trend,
        volatility,
    )

    # ======================================================
    # RISCO
    # ======================================================

    risk = determine_risk(
        volatility,
        score,
        trend,
    )

    # ======================================================
    # JUSTIFICATIVAS
    # ======================================================

    reasons = build_reasons(
        price,
        ma21,
        ma200,
        rsi,
        trend,
        risk,
    )

    # ======================================================
    # RESUMO EXECUTIVO
    # ======================================================

    executive_summary = build_executive_summary(
        asset,
        price,
        score,
        trend,
        risk,
        qualified_signal,
        recommendation,
        rsi,
    )

    # ======================================================
    # RETORNO FINAL
    # ======================================================

    return {

        "asset":
            asset,

        "price":
            price,

        "score":
            score,

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

        "reasons":
            reasons,

        "breakdown":
            breakdown,

        "executive_summary":
            executive_summary,

        "indicators": {

            "price":
                price,

            "ma21":
                ma21,

            "ma200":
                ma200,

            "rsi":
                rsi,

            "volatility":
                volatility,

        },

    }


# ==========================================================
# COMPATIBILIDADE
# ==========================================================

def get_analysis_summary(
    result,
):
    """
    Retorna somente os principais dados
    da análise.

    Função auxiliar para futuras versões
    do Dashboard.
    """

    if not isinstance(
        result,
        dict,
    ):

        return {}

    return {

        "score":
            result.get(
                "score"
            ),

        "classification":
            result.get(
                "classification"
            ),

        "signal":
            result.get(
                "qualified_signal",
                result.get(
                    "signal"
                ),
            ),

        "trend":
            result.get(
                "trend"
            ),

        "risk":
            result.get(
                "risk"
            ),

        "recommendation":
            result.get(
                "recommendation"
            ),

    }
