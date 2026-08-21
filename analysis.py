"""
InvestIA PRO
Motor de Análise

Versão: v0.7
Fase: 3.0.5 - Evolução Histórica da Análise

Responsabilidades:
- Executar análise técnica atual
- Consolidar Score Técnico
- Preservar Score Fundamentalista
- Consolidar Score Integrado
- Analisar histórico do Score Técnico
- Identificar evolução do Score
- Identificar mudanças de sinal
- Avaliar consistência do Score
- Gerar resumo executivo
"""

from score import (
    calculate_score_details,
    calculate_historical_score_analysis,
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

    return value


def safe_dict(
    value,
):
    """
    Garante o retorno de um dicionário.
    """

    if isinstance(
        value,
        dict,
    ):

        return value

    return {}


def safe_text(
    value,
    default="",
):
    """
    Converte valores para texto.
    """

    if value is None:

        return default

    text = str(
        value
    ).strip()

    if not text:

        return default

    return text


# ==========================================================
# STATUS DO RSI
# ==========================================================

def get_rsi_status(
    rsi,
):
    """
    Define o status do RSI.
    """

    rsi = safe_float(
        rsi
    )

    if rsi is None:

        return "Sem dados"

    if rsi <= 30:

        return "Sobrevendido"

    if rsi >= 70:

        return "Sobrecomprado"

    return "Neutro"


# ==========================================================
# TENDÊNCIA
# ==========================================================

def get_trend(
    price,
    ma21,
    ma200,
):
    """
    Define a tendência principal
    do ativo.
    """

    price = safe_float(
        price
    )

    ma21 = safe_float(
        ma21
    )

    ma200 = safe_float(
        ma200
    )

    if (
        price is None
        or ma21 is None
        or ma200 is None
    ):

        return "Indefinida"

    if (
        price > ma21
        and price > ma200
    ):

        return "Alta"

    if (
        price < ma21
        and price < ma200
    ):

        return "Baixa"

    if (
        price > ma200
        and price < ma21
    ):

        return "Correção"

    if (
        price < ma200
        and price > ma21
    ):

        return "Recuperação"

    return "Neutra"


# ==========================================================
# RECOMENDAÇÃO
# ==========================================================

def get_recommendation(
    signal,
    trend,
    risk,
):
    """
    Gera recomendação operacional.
    """

    signal = safe_text(
        signal
    ).upper()

    trend = safe_text(
        trend
    )

    risk = safe_text(
        risk
    )

    if (
        signal == "POSITIVO"
        and trend == "Alta"
        and risk != "Alto"
    ):

        return "Favorável"

    if (
        signal == "POSITIVO"
        and trend in [
            "Recuperação",
            "Neutra",
        ]
    ):

        return "Acompanhar oportunidade"

    if signal == "NEGATIVO":

        return "Evitar novas entradas"

    if risk == "Alto":

        return "Aguardar"

    return "Aguardar confirmação"


# ==========================================================
# RISCO TÉCNICO
# ==========================================================

def get_risk_level(
    volatility,
    signal,
):
    """
    Define o risco técnico com base
    na volatilidade e no sinal.
    """

    volatility = safe_float(
        volatility
    )

    signal = safe_text(
        signal
    ).upper()

    if volatility is None:

        return "Moderado"

    if volatility >= 0.04:

        return "Alto"

    if volatility >= 0.025:

        return "Moderado"

    if signal == "NEGATIVO":

        return "Moderado"

    return "Baixo"


# ==========================================================
# SCORE FUNDAMENTALISTA
# ==========================================================

def get_fundamental_score(
    data,
):
    """
    Obtém o Score Fundamentalista.

    Mantém compatibilidade com as fases
    anteriores do InvestIA PRO.

    Caso o dado não esteja disponível,
    retorna None.
    """

    data = safe_dict(
        data
    )

    possible_keys = [

        "fundamental_score",
        "score_fundamental",
        "fundamental",
        "fundamentalist_score",

    ]

    for key in possible_keys:

        value = safe_float(
            data.get(
                key
            )
        )

        if value is not None:

            return max(
                0,
                min(
                    100,
                    round(value),
                ),
            )

    return None


# ==========================================================
# SCORE INTEGRADO
# ==========================================================

def calculate_integrated_score(
    technical_score,
    fundamental_score=None,
):
    """
    Calcula o Score Integrado.

    Regra:

    Se houver Score Fundamentalista:

        60% Técnico
        40% Fundamentalista

    Caso contrário:

        Score Integrado = Score Técnico
    """

    technical_score = safe_float(
        technical_score
    )

    fundamental_score = safe_float(
        fundamental_score
    )

    if technical_score is None:

        return None

    if fundamental_score is None:

        return round(
            technical_score
        )

    integrated_score = (
        technical_score * 0.60
        + fundamental_score * 0.40
    )

    return max(
        0,
        min(
            100,
            round(
                integrated_score
            ),
        ),
    )


# ==========================================================
# CLASSIFICAÇÃO DO SCORE INTEGRADO
# ==========================================================

def classify_integrated_score(
    score,
):
    """
    Classifica o Score Integrado.
    """

    score = safe_float(
        score
    )

    if score is None:

        return "SEM DADOS"

    if score >= 80:

        return "MUITO FAVORÁVEL"

    if score >= 65:

        return "FAVORÁVEL"

    if score >= 50:

        return "NEUTRO"

    if score >= 35:

        return "DESFAVORÁVEL"

    return "MUITO DESFAVORÁVEL"


# ==========================================================
# JUSTIFICATIVAS TÉCNICAS
# ==========================================================

def build_reasons(
    price,
    ma21,
    ma200,
    rsi,
    trend,
    risk,
    score_details,
):
    """
    Constrói as justificativas
    da análise.
    """

    reasons = []

    price = safe_float(
        price
    )

    ma21 = safe_float(
        ma21
    )

    ma200 = safe_float(
        ma200
    )

    rsi = safe_float(
        rsi
    )

    score_details = safe_dict(
        score_details
    )

    breakdown = safe_dict(
        score_details.get(
            "breakdown"
        )
    )

    # ======================================================
    # MA21
    # ======================================================

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

    # ======================================================
    # MA200
    # ======================================================

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

    # ======================================================
    # RSI
    # ======================================================

    if rsi is not None:

        if rsi <= 30:

            reasons.append(
                "RSI indica região de sobrevenda."
            )

        elif rsi >= 70:

            reasons.append(
                "RSI indica região de sobrecompra."
            )

        else:

            reasons.append(
                "RSI permanece em região neutra."
            )

    # ======================================================
    # TENDÊNCIA
    # ======================================================

    reasons.append(
        f"Tendência técnica atual: {trend}."
    )

    # ======================================================
    # RISCO
    # ======================================================

    reasons.append(
        f"Nível de risco técnico: {risk}."
    )

    # ======================================================
    # BREAKDOWN
    # ======================================================

    for indicator in [
        "ma21",
        "ma200",
        "rsi",
    ]:

        indicator_data = safe_dict(
            breakdown.get(
                indicator
            )
        )

        reason = safe_text(
            indicator_data.get(
                "reason"
            )
        )

        if (
            reason
            and reason not in reasons
        ):

            reasons.append(
                reason
            )

    return reasons


# ==========================================================
# EVOLUÇÃO HISTÓRICA
# ==========================================================

def get_historical_analysis(
    data,
):
    """
    Obtém a análise histórica do Score Técnico.

    O DataFrame histórico pode ser recebido
    em uma das chaves abaixo:

    - historical
    - historical_indicators
    - indicators_history
    """

    data = safe_dict(
        data
    )

    historical_indicators = None

    possible_keys = [

        "historical",
        "historical_indicators",
        "indicators_history",

    ]

    for key in possible_keys:

        value = data.get(
            key
        )

        if value is not None:

            historical_indicators = value
            break

    if historical_indicators is None:

        return {

            "history": None,

            "summary": {},
        }

    try:

        historical_analysis = (
            calculate_historical_score_analysis(
                historical_indicators
            )
        )

    except Exception:

        return {

            "history": None,

            "summary": {},
        }

    if not isinstance(
        historical_analysis,
        dict,
    ):

        return {

            "history": None,

            "summary": {},
        }

    return {

        "history":
            historical_analysis.get(
                "history"
            ),

        "summary":
            safe_dict(
                historical_analysis.get(
                    "summary"
                )
            ),
    }


# ==========================================================
# INTERPRETAÇÃO DA EVOLUÇÃO
# ==========================================================

def get_evolution_interpretation(
    historical_summary,
):
    """
    Converte a evolução histórica
    em uma interpretação executiva.
    """

    historical_summary = safe_dict(
        historical_summary
    )

    evolution = safe_text(
        historical_summary.get(
            "evolution"
        ),
        "SEM DADOS",
    )

    variation = safe_float(
        historical_summary.get(
            "variation"
        )
    )

    consistency = safe_text(
        historical_summary.get(
            "consistency"
        ),
        "SEM DADOS",
    )

    if variation is None:

        return (
            "Histórico insuficiente para avaliar "
            "a evolução do Score."
        )

    if evolution == "MELHORANDO FORTE":

        return (
            f"O Score apresentou melhora relevante "
            f"de {variation:+.0f} pontos no período, "
            f"com consistência {consistency.lower()}."
        )

    if evolution == "MELHORANDO":

        return (
            f"O Score apresentou evolução positiva "
            f"de {variation:+.0f} pontos no período."
        )

    if evolution == "PIORANDO FORTE":

        return (
            f"O Score apresentou deterioração relevante "
            f"de {variation:.0f} pontos no período."
        )

    if evolution == "PIORANDO":

        return (
            f"O Score apresentou perda de força "
            f"de {variation:.0f} pontos no período."
        )

    return (
        "O Score permanece relativamente estável "
        "no período analisado."
    )


# ==========================================================
# RESUMO EXECUTIVO
# ==========================================================

def build_executive_summary(
    asset,
    technical_score,
    fundamental_score,
    integrated_score,
    trend,
    recommendation,
    risk,
    historical_summary,
):
    """
    Gera o resumo executivo final.
    """

    asset = safe_text(
        asset,
        "Ativo"
    )

    technical_score = safe_float(
        technical_score
    )

    fundamental_score = safe_float(
        fundamental_score
    )

    integrated_score = safe_float(
        integrated_score
    )

    trend = safe_text(
        trend,
        "Indefinida"
    )

    recommendation = safe_text(
        recommendation,
        "Aguardar"
    )

    risk = safe_text(
        risk,
        "Moderado"
    )

    summary = (
        f"{asset} apresenta tendência {trend.lower()}, "
        f"com Score Técnico de {technical_score:.0f}/100"
    )

    if fundamental_score is not None:

        summary += (
            f", Score Fundamentalista de "
            f"{fundamental_score:.0f}/100"
        )

    if integrated_score is not None:

        summary += (
            f" e Score Integrado de "
            f"{integrated_score:.0f}/100"
        )

    summary += (
        f". O risco atual é classificado como "
        f"{risk.lower()} e a recomendação é "
        f"{recommendation.lower()}."
    )

    evolution_text = get_evolution_interpretation(
        historical_summary
    )

    if evolution_text:

        summary += (
            f" {evolution_text}"
        )

    return summary


# ==========================================================
# ANÁLISE PRINCIPAL
# ==========================================================

def analyze_asset(
    data,
    asset=None,
):
    """
    Executa a análise completa do ativo.

    Entrada mínima:

    {
        "price": ...,
        "ma21": ...,
        "ma200": ...,
        "rsi": ...,
        "volatility": ...
    }

    Entrada opcional:

    {
        "fundamental_score": ...,
        "historical": DataFrame
    }
    """

    data = safe_dict(
        data
    )

    # ======================================================
    # IDENTIFICAÇÃO DO ATIVO
    # ======================================================

    if asset is None:

        asset = safe_text(
            data.get(
                "asset"
            ),
            "ATIVO",
        )

    else:

        asset = safe_text(
            asset,
            "ATIVO",
        )

    # ======================================================
    # DADOS TÉCNICOS
    # ======================================================

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

    volatility = safe_float(
        data.get(
            "volatility"
        )
    )

    required_values = [

        price,
        ma21,
        ma200,
        rsi,

    ]

    if any(
        value is None
        for value in required_values
    ):

        raise ValueError(
            "Dados técnicos insuficientes "
            "para analisar o ativo."
        )

    # ======================================================
    # SCORE TÉCNICO
    # ======================================================

    technical_data = {

        "price": price,

        "ma21": ma21,

        "ma200": ma200,

        "rsi": rsi,

    }

    score_details = calculate_score_details(
        technical_data
    )

    technical_score = safe_float(
        score_details.get(
            "technical_score"
        )
    )

    classification = safe_text(
        score_details.get(
            "classification"
        ),
        "NEUTRO",
    )

    signal = safe_text(
        score_details.get(
            "signal"
        ),
        "NEUTRO",
    )

    qualified_signal = safe_text(
        score_details.get(
            "qualified_signal"
        ),
        signal,
    )

    signal_level = safe_text(
        score_details.get(
            "signal_level"
        ),
        "Moderado",
    )

    signal_icon = safe_text(
        score_details.get(
            "signal_icon"
        ),
        "🟡",
    )

    breakdown = safe_dict(
        score_details.get(
            "breakdown"
        )
    )

    # ======================================================
    # TENDÊNCIA
    # ======================================================

    trend = get_trend(
        price,
        ma21,
        ma200,
    )

    # ======================================================
    # RSI
    # ======================================================

    rsi_status = get_rsi_status(
        rsi
    )

    # ======================================================
    # RISCO
    # ======================================================

    risk = get_risk_level(
        volatility,
        signal,
    )

    # ======================================================
    # FUNDAMENTALISTA
    # ======================================================

    fundamental_score = get_fundamental_score(
        data
    )

    # ======================================================
    # SCORE INTEGRADO
    # ======================================================

    integrated_score = calculate_integrated_score(
        technical_score,
        fundamental_score,
    )

    integrated_classification = (
        classify_integrated_score(
            integrated_score
        )
    )

    # ======================================================
    # HISTÓRICO
    # ======================================================

    historical_analysis = get_historical_analysis(
        data
    )

    score_history = historical_analysis.get(
        "history"
    )

    historical_summary = safe_dict(
        historical_analysis.get(
            "summary"
        )
    )

    evolution = safe_text(
        historical_summary.get(
            "evolution"
        ),
        "SEM DADOS",
    )

    score_variation = safe_float(
        historical_summary.get(
            "variation"
        )
    )

    consistency = safe_text(
        historical_summary.get(
            "consistency"
        ),
        "SEM DADOS",
    )

    signal_change = historical_summary.get(
        "signal_change"
    )

    if not isinstance(
        signal_change,
        dict,
    ):

        signal_change = {

            "changed": False,

            "previous": None,

            "current": signal,
        }

    # ======================================================
    # RECOMENDAÇÃO
    # ======================================================

    recommendation = get_recommendation(
        signal,
        trend,
        risk,
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
        score_details,
    )

    # ======================================================
    # RESUMO EXECUTIVO
    # ======================================================

    executive_summary = build_executive_summary(
        asset=asset,
        technical_score=technical_score,
        fundamental_score=fundamental_score,
        integrated_score=integrated_score,
        trend=trend,
        recommendation=recommendation,
        risk=risk,
        historical_summary=historical_summary,
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
        # SCORES
        # --------------------------------------------------

        "score":
            technical_score,

        "technical_score":
            technical_score,

        "fundamental_score":
            fundamental_score,

        "integrated_score":
            integrated_score,

        "integrated_classification":
            integrated_classification,

        # --------------------------------------------------
        # CLASSIFICAÇÃO
        # --------------------------------------------------

        "classification":
            classification,

        # --------------------------------------------------
        # SINAIS
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
        # ANÁLISE TÉCNICA
        # --------------------------------------------------

        "trend":
            trend,

        "tendencia":
            trend,

        "rsi_status":
            rsi_status,

        "risk":
            risk,

        "risco":
            risk,

        "recommendation":
            recommendation,

        "recomendacao":
            recommendation,

        # --------------------------------------------------
        # FUNDAMENTAÇÃO
        # --------------------------------------------------

        "reasons":
            reasons,

        "justificativas":
            reasons,

        "breakdown":
            breakdown,

        # --------------------------------------------------
        # HISTÓRICO
        # --------------------------------------------------

        "score_history":
            score_history,

        "historical_summary":
            historical_summary,

        "score_evolution":
            evolution,

        "score_variation":
            score_variation,

        "score_consistency":
            consistency,

        "signal_change":
            signal_change,

        # --------------------------------------------------
        # RESUMO
        # --------------------------------------------------

        "executive_summary":
            executive_summary,
    }
