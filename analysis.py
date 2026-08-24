"""
InvestIA PRO
Motor Principal de Análise

Versão: v0.7
Fase: 3.0.6 - Análise Fundamentalista Real

Responsabilidades:
- Receber dados técnicos e fundamentalistas
- Calcular Score Técnico
- Calcular Score Fundamentalista
- Calcular Score Integrado
- Identificar tendência
- Identificar condição do RSI
- Avaliar risco
- Gerar recomendação
- Criar resumo executivo
- Explicar os principais fatores da análise
"""

from score import (
    calculate_score_details,
    calculate_fundamental_score_details,
    calculate_integrated_score,
)


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def safe_float(
    value,
    default=None,
):
    """
    Converte um valor para float com segurança.
    """

    if value is None:
        return default

    try:
        value = float(value)

    except (
        TypeError,
        ValueError,
    ):
        return default

    if value != value:
        return default

    if value == float("inf"):
        return default

    if value == float("-inf"):
        return default

    return value


def safe_dict(
    value,
):
    """
    Garante que o retorno seja um dicionário.
    """

    if isinstance(
        value,
        dict,
    ):
        return value

    return {}


def get_value(
    data,
    *keys,
    default=None,
):
    """
    Busca um valor em um dicionário
    utilizando diferentes nomes possíveis.
    """

    if not isinstance(
        data,
        dict,
    ):
        return default

    for key in keys:

        if key in data:

            value = data.get(
                key
            )

            if value is not None:

                return value

    return default


def normalize_percent(
    value,
):
    """
    Normaliza valores percentuais.

    Exemplos:

    0.15 -> 15
    15   -> 15
    """

    value = safe_float(
        value
    )

    if value is None:
        return None

    if abs(value) <= 1:
        return value * 100

    return value


# ==========================================================
# TENDÊNCIA
# ==========================================================

def analyze_trend(
    data,
):
    """
    Analisa a tendência utilizando:

    - Preço
    - MA21
    - MA200
    """

    data = safe_dict(
        data
    )

    price = safe_float(
        get_value(
            data,
            "price",
        )
    )

    ma21 = safe_float(
        get_value(
            data,
            "ma21",
        )
    )

    ma200 = safe_float(
        get_value(
            data,
            "ma200",
        )
    )

    if (
        price is None
        or ma21 is None
        or ma200 is None
    ):

        return {
            "trend": "INDISPONÍVEL",
            "level": "Indisponível",
            "reason": (
                "Dados insuficientes para "
                "determinar a tendência."
            ),
        }

    # ======================================================
    # FORTE ALTA
    # ======================================================

    if (
        price > ma21
        and ma21 > ma200
    ):

        return {
            "trend": "ALTA",
            "level": "Forte",
            "reason": (
                "Preço acima da MA21 e "
                "MA21 acima da MA200."
            ),
        }

    # ======================================================
    # ALTA
    # ======================================================

    if (
        price > ma21
        and price > ma200
    ):

        return {
            "trend": "ALTA",
            "level": "Moderada",
            "reason": (
                "Preço acima das principais "
                "médias móveis."
            ),
        }

    # ======================================================
    # BAIXA
    # ======================================================

    if (
        price < ma21
        and price < ma200
    ):

        return {
            "trend": "BAIXA",
            "level": "Forte",
            "reason": (
                "Preço abaixo da MA21 e "
                "da MA200."
            ),
        }

    # ======================================================
    # TRANSIÇÃO
    # ======================================================

    return {
        "trend": "LATERAL",
        "level": "Transição",
        "reason": (
            "Preço sem alinhamento claro "
            "entre as médias móveis."
        ),
    }


# ==========================================================
# STATUS DO RSI
# ==========================================================

def analyze_rsi(
    data,
):
    """
    Classifica a condição do RSI.

    Faixas:

    <= 30  : Sobrevendido
    <= 45  : Pressão vendedora
    < 55   : Neutro
    < 70   : Pressão compradora
    >= 70  : Sobrecomprado
    """

    data = safe_dict(
        data
    )

    rsi = safe_float(
        get_value(
            data,
            "rsi",
        )
    )

    if rsi is None:

        return {
            "status": "INDISPONÍVEL",
            "value": None,
            "reason": (
                "RSI não disponível."
            ),
        }

    if rsi <= 30:

        return {
            "status": "SOBREVENDIDO",
            "value": rsi,
            "reason": (
                "RSI em região de sobrevenda."
            ),
        }

    if rsi <= 45:

        return {
            "status": "PRESSÃO VENDEDORA",
            "value": rsi,
            "reason": (
                "RSI abaixo da região neutra."
            ),
        }

    if rsi < 55:

        return {
            "status": "NEUTRO",
            "value": rsi,
            "reason": (
                "RSI em região neutra."
            ),
        }

    if rsi < 70:

        return {
            "status": "PRESSÃO COMPRADORA",
            "value": rsi,
            "reason": (
                "RSI demonstra força compradora."
            ),
        }

    return {
        "status": "SOBRECOMPRADO",
        "value": rsi,
        "reason": (
            "RSI em região de sobrecompra."
        ),
    }


# ==========================================================
# ANÁLISE DE RISCO
# ==========================================================

def analyze_risk(
    data,
    technical_score,
    fundamental_score,
    integrated_score,
):
    """
    Avalia o risco geral do ativo.

    Considera:

    - Volatilidade
    - Score Técnico
    - Score Fundamentalista
    - Score Integrado
    """

    data = safe_dict(
        data
    )

    volatility = safe_float(
        get_value(
            data,
            "volatility",
        )
    )

    technical_score = safe_float(
        technical_score,
        50,
    )

    fundamental_score = safe_float(
        fundamental_score,
        50,
    )

    integrated_score = safe_float(
        integrated_score,
        50,
    )

    risk_points = 0
    reasons = []

    # ======================================================
    # VOLATILIDADE
    # ======================================================

    if volatility is not None:

        if volatility >= 0.04:

            risk_points += 3

            reasons.append(
                "Volatilidade elevada."
            )

        elif volatility >= 0.025:

            risk_points += 2

            reasons.append(
                "Volatilidade moderada."
            )

        else:

            reasons.append(
                "Volatilidade controlada."
            )

    # ======================================================
    # SCORE TÉCNICO
    # ======================================================

    if technical_score < 35:

        risk_points += 2

        reasons.append(
            "Score Técnico fraco."
        )

    elif technical_score < 50:

        risk_points += 1

        reasons.append(
            "Score Técnico abaixo do neutro."
        )

    # ======================================================
    # SCORE FUNDAMENTALISTA
    # ======================================================

    if fundamental_score < 35:

        risk_points += 2

        reasons.append(
            "Fundamentos fracos."
        )

    elif fundamental_score < 50:

        risk_points += 1

        reasons.append(
            "Fundamentos abaixo do neutro."
        )

    # ======================================================
    # SCORE INTEGRADO
    # ======================================================

    if integrated_score < 35:

        risk_points += 2

        reasons.append(
            "Score Integrado muito fraco."
        )

    elif integrated_score < 50:

        risk_points += 1

        reasons.append(
            "Score Integrado abaixo do neutro."
        )

    # ======================================================
    # CLASSIFICAÇÃO
    # ======================================================

    if risk_points >= 6:

        level = "ALTO"

    elif risk_points >= 3:

        level = "MODERADO"

    else:

        level = "BAIXO"

    return {
        "level": level,
        "points": risk_points,
        "volatility": volatility,
        "reasons": reasons,
    }


# ==========================================================
# RECOMENDAÇÃO
# ==========================================================

def generate_recommendation(
    integrated_score,
    technical_score,
    fundamental_score,
    trend,
    risk_level,
):
    """
    Gera uma recomendação baseada
    no conjunto da análise.
    """

    integrated_score = safe_float(
        integrated_score,
        50,
    )

    technical_score = safe_float(
        technical_score,
        50,
    )

    fundamental_score = safe_float(
        fundamental_score,
        50,
    )

    trend = str(
        trend
        or ""
    ).upper()

    risk_level = str(
        risk_level
        or ""
    ).upper()

    # ======================================================
    # COMPRA FORTE
    # ======================================================

    if (
        integrated_score >= 75
        and technical_score >= 65
        and fundamental_score >= 65
        and trend == "ALTA"
        and risk_level != "ALTO"
    ):

        return {
            "recommendation": "COMPRA FORTE",
            "signal_level": "ALTO",
            "reason": (
                "Indicadores técnicos e "
                "fundamentalistas apresentam "
                "alinhamento positivo."
            ),
        }

    # ======================================================
    # COMPRA
    # ======================================================

    if (
        integrated_score >= 65
        and fundamental_score >= 50
        and risk_level != "ALTO"
    ):

        return {
            "recommendation": "COMPRA",
            "signal_level": "MODERADO",
            "reason": (
                "Score Integrado favorável, "
                "com fundamentos aceitáveis."
            ),
        }

    # ======================================================
    # COMPRA COM CAUTELA
    # ======================================================

    if (
        integrated_score >= 55
        and fundamental_score >= 45
    ):

        return {
            "recommendation": "COMPRA COM CAUTELA",
            "signal_level": "BAIXO",
            "reason": (
                "Cenário levemente favorável, "
                "mas sem confirmação forte "
                "de todos os indicadores."
            ),
        }

    # ======================================================
    # VENDA FORTE
    # ======================================================

    if (
        integrated_score <= 30
        and technical_score <= 35
        and fundamental_score <= 35
        and risk_level == "ALTO"
    ):

        return {
            "recommendation": "VENDA FORTE",
            "signal_level": "ALTO",
            "reason": (
                "Indicadores técnicos e "
                "fundamentalistas apresentam "
                "fraqueza relevante."
            ),
        }

    # ======================================================
    # VENDA
    # ======================================================

    if integrated_score <= 40:

        return {
            "recommendation": "VENDA",
            "signal_level": "MODERADO",
            "reason": (
                "Score Integrado desfavorável."
            ),
        }

    # ======================================================
    # NEUTRO
    # ======================================================

    return {
        "recommendation": "AGUARDAR",
        "signal_level": "NEUTRO",
        "reason": (
            "Não há alinhamento suficiente "
            "para uma recomendação direcional forte."
        ),
    }


# ==========================================================
# QUALIFICAÇÃO DO SINAL
# ==========================================================

def qualify_signal(
    recommendation,
    integrated_score,
    risk_level,
):
    """
    Define uma qualificação adicional
    para o sinal principal.
    """

    recommendation = str(
        recommendation
        or ""
    ).upper()

    integrated_score = safe_float(
        integrated_score,
        50,
    )

    risk_level = str(
        risk_level
        or ""
    ).upper()

    if risk_level == "ALTO":

        return "ALTA CAUTELA"

    if recommendation == "COMPRA FORTE":

        return "SINAL MUITO FORTE"

    if recommendation == "COMPRA":

        if integrated_score >= 75:

            return "SINAL FORTE"

        return "SINAL FAVORÁVEL"

    if recommendation == "COMPRA COM CAUTELA":

        return "SINAL EM FORMAÇÃO"

    if recommendation == "VENDA FORTE":

        return "SINAL MUITO NEGATIVO"

    if recommendation == "VENDA":

        return "SINAL NEGATIVO"

    return "SEM CONFIRMAÇÃO"


# ==========================================================
# ÍCONE DO SINAL
# ==========================================================

def get_signal_icon(
    recommendation,
):
    """
    Retorna um ícone para a interface.
    """

    recommendation = str(
        recommendation
        or ""
    ).upper()

    icons = {

        "COMPRA FORTE": "🟢",

        "COMPRA": "🟩",

        "COMPRA COM CAUTELA": "🟡",

        "AGUARDAR": "⚪",

        "VENDA": "🟠",

        "VENDA FORTE": "🔴",
    }

    return icons.get(
        recommendation,
        "⚪",
    )


# ==========================================================
# RAZÕES PRINCIPAIS
# ==========================================================

def get_analysis_reasons(
    technical_details,
    fundamental_details,
    trend_data,
    rsi_data,
    risk_data,
    recommendation_data,
):
    """
    Gera uma lista consolidada dos
    principais fatores da análise.
    """

    reasons = []

    # ======================================================
    # TENDÊNCIA
    # ======================================================

    trend_reason = get_value(
        trend_data,
        "reason",
    )

    if trend_reason:
        reasons.append(
            trend_reason
        )

    # ======================================================
    # RSI
    # ======================================================

    rsi_reason = get_value(
        rsi_data,
        "reason",
    )

    if rsi_reason:
        reasons.append(
            rsi_reason
        )

    # ======================================================
    # FUNDAMENTALISTA
    # ======================================================

    fundamental_breakdown = get_value(
        fundamental_details,
        "breakdown",
        default={},
    )

    fundamental_breakdown = safe_dict(
        fundamental_breakdown
    )

    positive_fundamentals = []
    negative_fundamentals = []

    indicators = [

        "price_to_earnings",
        "price_to_book",
        "return_on_equity",
        "dividend_yield",
        "profit_margin",
        "revenue_growth",
        "debt_to_equity",
    ]

    for indicator in indicators:

        item = safe_dict(
            fundamental_breakdown.get(
                indicator
            )
        )

        points = safe_float(
            item.get(
                "points"
            ),
            0,
        )

        reason = item.get(
            "reason"
        )

        if not reason:
            continue

        if points > 0:

            positive_fundamentals.append(
                (
                    points,
                    reason,
                )
            )

        elif points < 0:

            negative_fundamentals.append(
                (
                    points,
                    reason,
                )
            )

    positive_fundamentals.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    negative_fundamentals.sort(
        key=lambda item: item[0],
    )

    for _, reason in positive_fundamentals[:2]:

        reasons.append(
            reason
        )

    for _, reason in negative_fundamentals[:2]:

        reasons.append(
            reason
        )

    # ======================================================
    # RISCO
    # ======================================================

    risk_level = get_value(
        risk_data,
        "level",
    )

    if risk_level:

        reasons.append(
            f"Classificação de risco: {risk_level}."
        )

    # ======================================================
    # RECOMENDAÇÃO
    # ======================================================

    recommendation_reason = get_value(
        recommendation_data,
        "reason",
    )

    if recommendation_reason:

        reasons.append(
            recommendation_reason
        )

    return reasons


# ==========================================================
# RESUMO EXECUTIVO
# ==========================================================

def generate_executive_summary(
    asset,
    technical_score,
    fundamental_score,
    integrated_score,
    technical_classification,
    fundamental_classification,
    trend,
    risk_level,
    recommendation,
    fundamental_coverage,
):
    """
    Gera o resumo executivo final.
    """

    asset = str(
        asset
        or "ATIVO"
    ).upper()

    technical_score = safe_float(
        technical_score,
        0,
    )

    fundamental_score = safe_float(
        fundamental_score,
        0,
    )

    integrated_score = safe_float(
        integrated_score,
        0,
    )

    coverage = safe_float(
        fundamental_coverage,
        0,
    )

    summary = (
        f"{asset}: Score Técnico de "
        f"{technical_score:.0f}/100 "
        f"({technical_classification}), "
        f"Score Fundamentalista de "
        f"{fundamental_score:.0f}/100 "
        f"({fundamental_classification}) "
        f"e Score Integrado de "
        f"{integrated_score:.0f}/100. "
        f"A tendência identificada é "
        f"{trend}, com risco {risk_level}. "
        f"A recomendação atual é "
        f"{recommendation}."
    )

    if coverage < 50:

        summary += (
            " A cobertura dos dados "
            "fundamentalistas é limitada, "
            "portanto o resultado deve ser "
            "interpretado com cautela."
        )

    elif coverage < 80:

        summary += (
            f" A análise fundamentalista possui "
            f"cobertura de {coverage:.0f}% "
            f"dos indicadores avaliados."
        )

    else:

        summary += (
            f" A análise fundamentalista possui "
            f"boa cobertura de dados "
            f"({coverage:.0f}%)."
        )

    return summary


# ==========================================================
# ANÁLISE PRINCIPAL
# ==========================================================

def analyze_asset(
    data,
    asset=None,
    technical_weight=0.50,
    fundamental_weight=0.50,
):
    """
    Executa a análise completa do InvestIA PRO.

    Estrutura esperada:

    {
        "price": ...,
        "ma21": ...,
        "ma200": ...,
        "rsi": ...,
        "volatility": ...,
        "fundamentals": {
            ...
        }
    }

    Retorno:

    - Score Técnico
    - Score Fundamentalista
    - Score Integrado
    - Tendência
    - RSI
    - Risco
    - Recomendação
    - Explicabilidade
    - Resumo Executivo
    """

    if not isinstance(
        data,
        dict,
    ):

        raise ValueError(
            "Dados inválidos para análise."
        )

    # ======================================================
    # ATIVO
    # ======================================================

    if asset is None:

        asset = get_value(
            data,
            "asset",
            "ticker",
            default="ATIVO",
        )

    asset = str(
        asset
        or "ATIVO"
    ).upper()

    # ======================================================
    # FUNDAMENTOS
    # ======================================================

    fundamentals = get_value(
        data,
        "fundamentals",
        default={},
    )

    fundamentals = safe_dict(
        fundamentals
    )

    # ======================================================
    # DADOS TÉCNICOS
    # ======================================================

    technical_data = {

        "price":
            get_value(
                data,
                "price",
            ),

        "ma21":
            get_value(
                data,
                "ma21",
            ),

        "ma200":
            get_value(
                data,
                "ma200",
            ),

        "rsi":
            get_value(
                data,
                "rsi",
            ),
    }

    # ======================================================
    # SCORE TÉCNICO
    # ======================================================

    technical_details = calculate_score_details(
        technical_data
    )

    technical_score = technical_details[
        "score"
    ]

    technical_classification = (
        technical_details[
            "classification"
        ]
    )

    technical_signal = technical_details[
        "signal"
    ]

    # ======================================================
    # SCORE FUNDAMENTALISTA
    # ======================================================

    fundamental_details = (
        calculate_fundamental_score_details(
            fundamentals
        )
    )

    fundamental_score = fundamental_details[
        "score"
    ]

    fundamental_classification = (
        fundamental_details[
            "classification"
        ]
    )

    fundamental_signal = fundamental_details[
        "signal"
    ]

    fundamental_coverage = (
        fundamental_details.get(
            "coverage",
            0,
        )
    )

    # ======================================================
    # SCORE INTEGRADO
    # ======================================================

    integrated_details = calculate_integrated_score(

        technical_score,
        fundamental_score,

        technical_weight=
            technical_weight,

        fundamental_weight=
            fundamental_weight,
    )

    integrated_score = integrated_details[
        "score"
    ]

    integrated_classification = (
        integrated_details[
            "classification"
        ]
    )

    integrated_signal = (
        integrated_details[
            "signal"
        ]
    )

    # ======================================================
    # TENDÊNCIA
    # ======================================================

    trend_data = analyze_trend(
        technical_data
    )

    trend = trend_data[
        "trend"
    ]

    trend_level = trend_data[
        "level"
    ]

    # ======================================================
    # RSI
    # ======================================================

    rsi_data = analyze_rsi(
        technical_data
    )

    rsi_status = rsi_data[
        "status"
    ]

    # ======================================================
    # RISCO
    # ======================================================

    risk_data = analyze_risk(

        data=data,

        technical_score=
            technical_score,

        fundamental_score=
            fundamental_score,

        integrated_score=
            integrated_score,
    )

    risk_level = risk_data[
        "level"
    ]

    # ======================================================
    # RECOMENDAÇÃO
    # ======================================================

    recommendation_data = generate_recommendation(

        integrated_score=
            integrated_score,

        technical_score=
            technical_score,

        fundamental_score=
            fundamental_score,

        trend=
            trend,

        risk_level=
            risk_level,
    )

    recommendation = recommendation_data[
        "recommendation"
    ]

    signal_level = recommendation_data[
        "signal_level"
    ]

    # ======================================================
    # QUALIFICAÇÃO DO SINAL
    # ======================================================

    qualified_signal = qualify_signal(

        recommendation=
            recommendation,

        integrated_score=
            integrated_score,

        risk_level=
            risk_level,
    )

    signal_icon = get_signal_icon(
        recommendation
    )

    # ======================================================
    # RAZÕES
    # ======================================================

    reasons = get_analysis_reasons(

        technical_details=
            technical_details,

        fundamental_details=
            fundamental_details,

        trend_data=
            trend_data,

        rsi_data=
            rsi_data,

        risk_data=
            risk_data,

        recommendation_data=
            recommendation_data,
    )

    # ======================================================
    # RESUMO EXECUTIVO
    # ======================================================

    executive_summary = (
        generate_executive_summary(

            asset=
                asset,

            technical_score=
                technical_score,

            fundamental_score=
                fundamental_score,

            integrated_score=
                integrated_score,

            technical_classification=
                technical_classification,

            fundamental_classification=
                fundamental_classification,

            trend=
                trend,

            risk_level=
                risk_level,

            recommendation=
                recommendation,

            fundamental_coverage=
                fundamental_coverage,
        )
    )

    # ======================================================
    # RETORNO FINAL
    # ======================================================

    return {

        # --------------------------------------------------
        # ATIVO
        # --------------------------------------------------

        "asset":
            asset,

        # --------------------------------------------------
        # SCORE TÉCNICO
        # --------------------------------------------------

        "technical_score":
            technical_score,

        "technical_classification":
            technical_classification,

        "technical_signal":
            technical_signal,

        "technical_breakdown":
            technical_details.get(
                "breakdown",
                {}
            ),

        # --------------------------------------------------
        # SCORE FUNDAMENTALISTA
        # --------------------------------------------------

        "fundamental_score":
            fundamental_score,

        "fundamental_classification":
            fundamental_classification,

        "fundamental_signal":
            fundamental_signal,

        "fundamental_coverage":
            fundamental_coverage,

        "fundamental_available_indicators":
            fundamental_details.get(
                "available_indicators",
                0,
            ),

        "fundamental_total_indicators":
            fundamental_details.get(
                "total_indicators",
                0,
            ),

        "fundamental_breakdown":
            fundamental_details.get(
                "breakdown",
                {}
            ),

        # --------------------------------------------------
        # SCORE INTEGRADO
        # --------------------------------------------------

        "score":
            integrated_score,

        "integrated_score":
            integrated_score,

        "classification":
            integrated_classification,

        "integrated_classification":
            integrated_classification,

        "signal":
            integrated_signal,

        "integrated_signal":
            integrated_signal,

        "score_details":
            integrated_details,

        # --------------------------------------------------
        # TENDÊNCIA
        # --------------------------------------------------

        "trend":
            trend,

        "trend_level":
            trend_level,

        "trend_reason":
            trend_data.get(
                "reason"
            ),

        # --------------------------------------------------
        # RSI
        # --------------------------------------------------

        "rsi_status":
            rsi_status,

        "rsi_data":
            rsi_data,

        # --------------------------------------------------
        # RISCO
        # --------------------------------------------------

        "risk":
            risk_level,

        "risk_data":
            risk_data,

        # --------------------------------------------------
        # RECOMENDAÇÃO
        # --------------------------------------------------

        "recommendation":
            recommendation,

        "signal_level":
            signal_level,

        "qualified_signal":
            qualified_signal,

        "signal_icon":
            signal_icon,

        # --------------------------------------------------
        # EXPLICABILIDADE
        # --------------------------------------------------

        "reasons":
            reasons,

        # --------------------------------------------------
        # RESUMO
        # --------------------------------------------------

        "executive_summary":
            executive_summary,
    }
