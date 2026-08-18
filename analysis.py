"""
InvestIA PRO
Motor de Análise

Versão: v0.6
Fase: 2.9.3 - Confiabilidade do Score
"""

from score import (
    calculate_score_details,
    classify_score,
    classify_signal,
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


def _normalize_text(
    value,
    default="N/A",
):
    """
    Normaliza textos retornados pela análise.
    """

    if value is None:
        return default

    value = str(
        value
    ).strip()

    if not value:
        return default

    return value


# ==========================================================
# VALIDAÇÃO DOS DADOS
# ==========================================================

def validate_analysis_input(data):
    """
    Valida os dados necessários para executar
    a análise do ativo.
    """

    required = [
        "price",
        "rsi",
        "ma21",
        "ma200",
        "volatility",
    ]

    if data is None:

        return {

            "valid": False,

            "missing": required,

            "message":
                "Dados não fornecidos para análise.",

        }

    if not isinstance(
        data,
        dict,
    ):

        return {

            "valid": False,

            "missing": required,

            "message":
                "Formato de dados inválido para análise.",

        }

    missing = []

    for field in required:

        value = data.get(
            field
        )

        if value is None:

            missing.append(
                field
            )

            continue

        try:

            float(value)

        except (
            TypeError,
            ValueError,
        ):

            missing.append(
                field
            )

    if missing:

        return {

            "valid": False,

            "missing": missing,

            "message":
                "Dados insuficientes para análise: "
                + ", ".join(missing)
                + ".",

        }

    return {

        "valid": True,

        "missing": [],

        "message":
            "Dados suficientes para análise.",

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
    Determina a tendência utilizando
    preço, MA21 e MA200.
    """

    price = _safe_float(
        price
    )

    ma21 = _safe_float(
        ma21
    )

    ma200 = _safe_float(
        ma200
    )

    if (
        price is None
        or ma21 is None
        or ma200 is None
    ):

        return "Indisponível"

    # ------------------------------------------------------
    # TENDÊNCIA DE ALTA
    # ------------------------------------------------------

    if (
        price > ma21
        and price > ma200
        and ma21 > ma200
    ):

        return "Alta"

    # ------------------------------------------------------
    # TENDÊNCIA DE BAIXA
    # ------------------------------------------------------

    if (
        price < ma21
        and price < ma200
        and ma21 < ma200
    ):

        return "Baixa"

    # ------------------------------------------------------
    # TENDÊNCIA POSITIVA
    # ------------------------------------------------------

    if (
        price > ma21
        and price > ma200
    ):

        return "Alta Moderada"

    # ------------------------------------------------------
    # TENDÊNCIA NEGATIVA
    # ------------------------------------------------------

    if (
        price < ma21
        and price < ma200
    ):

        return "Baixa Moderada"

    # ------------------------------------------------------
    # TRANSIÇÃO
    # ------------------------------------------------------

    return "Transição"


# ==========================================================
# STATUS DO RSI
# ==========================================================

def determine_rsi_status(
    rsi,
):
    """
    Classifica o RSI.
    """

    rsi = _safe_float(
        rsi
    )

    if rsi is None:

        return "Indisponível"

    if rsi <= 30:

        return "Sobrevenda"

    if rsi >= 70:

        return "Sobrecompra"

    if rsi >= 50:

        return "Neutro / Positivo"

    return "Neutro / Negativo"


# ==========================================================
# RISCO
# ==========================================================

def determine_risk(
    volatility,
    score,
):
    """
    Classifica o risco considerando volatilidade
    e Score.
    """

    volatility = _safe_float(
        volatility
    )

    score = _safe_float(
        score
    )

    if (
        volatility is None
        or score is None
    ):

        return "Indisponível"

    volatility_percent = (
        volatility * 100
    )

    # ------------------------------------------------------
    # ALTO
    # ------------------------------------------------------

    if volatility_percent >= 4:

        return "Alto"

    # ------------------------------------------------------
    # MODERADO
    # ------------------------------------------------------

    if volatility_percent >= 2:

        return "Moderado"

    # ------------------------------------------------------
    # SCORE MUITO FRACO
    # ------------------------------------------------------

    if score < 35:

        return "Alto"

    # ------------------------------------------------------
    # BAIXO
    # ------------------------------------------------------

    return "Baixo"


# ==========================================================
# RECOMENDAÇÃO
# ==========================================================

def determine_recommendation(
    score,
    signal,
    trend,
):
    """
    Determina a recomendação final.

    A recomendação somente é gerada
    quando o Score é confiável.
    """

    if score is None:

        return "Indisponível"

    signal = _normalize_text(
        signal,
        "NEUTRO",
    )

    trend = _normalize_text(
        trend,
        "Indisponível",
    )

    # ------------------------------------------------------
    # SINAL POSITIVO
    # ------------------------------------------------------

    if signal == "POSITIVO":

        if trend in [
            "Alta",
            "Alta Moderada",
        ]:

            return "Compra"

        return "Aguardar confirmação"

    # ------------------------------------------------------
    # SINAL NEGATIVO
    # ------------------------------------------------------

    if signal == "NEGATIVO":

        if trend in [
            "Baixa",
            "Baixa Moderada",
        ]:

            return "Venda / Redução"

        return "Aguardar confirmação"

    # ------------------------------------------------------
    # NEUTRO
    # ------------------------------------------------------

    return "Aguardar"


# ==========================================================
# SINAL QUALIFICADO
# ==========================================================

def determine_qualified_signal(
    signal,
    trend,
):
    """
    Qualifica o sinal considerando a tendência.
    """

    signal = _normalize_text(
        signal,
        "NEUTRO",
    )

    trend = _normalize_text(
        trend,
        "Indisponível",
    )

    if signal == "POSITIVO":

        if trend == "Alta":

            return "COMPRA FORTE"

        if trend == "Alta Moderada":

            return "COMPRA"

        return "POSITIVO"

    if signal == "NEGATIVO":

        if trend == "Baixa":

            return "VENDA FORTE"

        if trend == "Baixa Moderada":

            return "VENDA"

        return "NEGATIVO"

    return "NEUTRO"


# ==========================================================
# NÍVEL DO SINAL
# ==========================================================

def determine_signal_level(
    score,
):
    """
    Determina a intensidade do sinal.
    """

    score = _safe_float(
        score
    )

    if score is None:

        return "Indisponível"

    if score >= 80:

        return "Muito forte"

    if score >= 65:

        return "Forte"

    if score >= 50:

        return "Moderado"

    if score >= 35:

        return "Fraco"

    return "Muito fraco"


# ==========================================================
# ÍCONE DO SINAL
# ==========================================================

def get_signal_icon(
    signal,
):
    """
    Retorna o ícone correspondente ao sinal.
    """

    signal = _normalize_text(
        signal,
        "NEUTRO",
    ).upper()

    if "POSITIVO" in signal:

        return "🟢"

    if "COMPRA" in signal:

        return "🟢"

    if "NEGATIVO" in signal:

        return "🔴"

    if "VENDA" in signal:

        return "🔴"

    return "🟡"


# ==========================================================
# JUSTIFICATIVAS
# ==========================================================

def build_reasons(
    data,
    breakdown,
    trend,
    rsi_status,
):
    """
    Constrói as justificativas da análise.
    """

    reasons = []

    if not isinstance(
        breakdown,
        dict,
    ):

        return reasons

    # ------------------------------------------------------
    # MA21
    # ------------------------------------------------------

    ma21 = breakdown.get(
        "ma21",
        {},
    )

    if isinstance(
        ma21,
        dict,
    ):

        reason = ma21.get(
            "reason"
        )

        if reason:

            reasons.append(
                reason
            )

    # ------------------------------------------------------
    # MA200
    # ------------------------------------------------------

    ma200 = breakdown.get(
        "ma200",
        {},
    )

    if isinstance(
        ma200,
        dict,
    ):

        reason = ma200.get(
            "reason"
        )

        if reason:

            reasons.append(
                reason
            )

    # ------------------------------------------------------
    # RSI
    # ------------------------------------------------------

    rsi = breakdown.get(
        "rsi",
        {},
    )

    if isinstance(
        rsi,
        dict,
    ):

        reason = rsi.get(
            "reason"
        )

        if reason:

            reasons.append(
                reason
            )

    # ------------------------------------------------------
    # TENDÊNCIA
    # ------------------------------------------------------

    if trend:

        reasons.append(
            f"Tendência identificada: {trend}."
        )

    # ------------------------------------------------------
    # RSI STATUS
    # ------------------------------------------------------

    if rsi_status:

        reasons.append(
            f"Status do RSI: {rsi_status}."
        )

    return reasons


# ==========================================================
# RESUMO EXECUTIVO
# ==========================================================

def build_executive_summary(
    asset,
    score,
    classification,
    signal,
    trend,
    risk,
    recommendation,
):
    """
    Gera o resumo executivo da análise.
    """

    asset = _normalize_text(
        asset,
        "Ativo",
    )

    if score is None:

        return (
            f"{asset}: não foi possível gerar "
            "uma conclusão confiável porque "
            "os dados necessários para o Score "
            "estão incompletos."
        )

    return (
        f"{asset} apresenta Score InvestIA de "
        f"{score}/100, classificado como "
        f"{classification}. "
        f"A tendência atual é {trend}, "
        f"com sinal {signal}. "
        f"O nível de risco é {risk} "
        f"e a recomendação é "
        f"{recommendation}."
    )


# ==========================================================
# ANÁLISE INDEFINIDA
# ==========================================================

def build_unreliable_analysis(
    asset,
    validation,
    score_details,
):
    """
    Retorna uma análise segura quando os dados
    não são suficientes para gerar um Score confiável.
    """

    missing = validation.get(
        "missing",
        [],
    )

    invalid = validation.get(
        "invalid",
        [],
    )

    if missing:

        data_problem = (
            "Indicadores ausentes: "
            + ", ".join(missing)
            + "."
        )

    elif invalid:

        data_problem = (
            "Indicadores inválidos: "
            + ", ".join(invalid)
            + "."
        )

    else:

        data_problem = (
            "Os dados disponíveis não "
            "foram considerados suficientes."
        )

    return {

        "asset":
            asset,

        "score":
            None,

        "classification":
            "INDEFINIDO",

        "signal":
            "INDEFINIDO",

        "qualified_signal":
            "INDEFINIDO",

        "signal_level":
            "Indisponível",

        "signal_icon":
            "⚪",

        "trend":
            "Indisponível",

        "recommendation":
            "Aguardar dados",

        "risk":
            "Indisponível",

        "rsi_status":
            "Indisponível",

        "reasons": [

            "A análise não possui "
            "dados suficientes para "
            "uma conclusão confiável.",

            data_problem,

        ],

        "breakdown":
            {},

        "executive_summary":
            (
                f"{asset}: análise não disponível. "
                f"{data_problem}"
            ),

        "score_reliable":
            False,

        "reliable":
            False,

        "analysis_reliable":
            False,

        "validation":
            validation,

        "score_validation":
            score_details.get(
                "validation",
                validation,
            ),

        "missing_indicators":
            missing,

        "invalid_indicators":
            invalid,

        "status":
            "DADOS INSUFICIENTES",

        "status_icon":
            "🔴",

        "status_message":
            (
                "O Score não deve ser utilizado "
                "para tomada de decisão enquanto "
                "os dados estiverem incompletos."
            ),

    }


# ==========================================================
# ANÁLISE PRINCIPAL
# ==========================================================

def analyze_asset(
    data,
    asset=None,
):
    """
    Executa a análise completa do ativo.

    Fluxo:

        1. Validação dos dados
        2. Cálculo do Score
        3. Validação da confiabilidade
        4. Tendência
        5. RSI
        6. Risco
        7. Recomendação
        8. Justificativas
        9. Resumo executivo
    """

    # ======================================================
    # ATIVO
    # ======================================================

    if asset is None:

        if isinstance(
            data,
            dict,
        ):

            asset = data.get(
                "asset"
            )

    asset = _normalize_text(
        asset,
        "ATIVO",
    ).upper()

    # ======================================================
    # VALIDAÇÃO
    # ======================================================

    validation = validate_analysis_input(
        data
    )

    # ======================================================
    # SCORE
    # ======================================================

    score_details = calculate_score_details(
        data
    )

    # ======================================================
    # SCORE NÃO CONFIÁVEL
    # ======================================================

    if not score_details.get(
        "score_reliable",
        False,
    ):

        return build_unreliable_analysis(
            asset,
            score_details.get(
                "validation",
                validation,
            ),
            score_details,
        )

    # ======================================================
    # SCORE CONFIÁVEL
    # ======================================================

    score = score_details.get(
        "score"
    )

    classification = score_details.get(
        "classification"
    )

    signal = score_details.get(
        "signal"
    )

    breakdown = score_details.get(
        "breakdown",
        {},
    )

    # ======================================================
    # INDICADORES
    # ======================================================

    price = _safe_float(
        data.get(
            "price"
        )
    )

    ma21 = _safe_float(
        data.get(
            "ma21"
        )
    )

    ma200 = _safe_float(
        data.get(
            "ma200"
        )
    )

    rsi = _safe_float(
        data.get(
            "rsi"
        )
    )

    volatility = _safe_float(
        data.get(
            "volatility"
        )
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
    # RISCO
    # ======================================================

    risk = determine_risk(
        volatility,
        score,
    )

    # ======================================================
    # RECOMENDAÇÃO
    # ======================================================

    recommendation = determine_recommendation(
        score,
        signal,
        trend,
    )

    # ======================================================
    # SINAL QUALIFICADO
    # ======================================================

    qualified_signal = determine_qualified_signal(
        signal,
        trend,
    )

    # ======================================================
    # NÍVEL
    # ======================================================

    signal_level = determine_signal_level(
        score
    )

    # ======================================================
    # ÍCONE
    # ======================================================

    signal_icon = get_signal_icon(
        qualified_signal
    )

    # ======================================================
    # JUSTIFICATIVAS
    # ======================================================

    reasons = build_reasons(
        data,
        breakdown,
        trend,
        rsi_status,
    )

    # ======================================================
    # RESUMO EXECUTIVO
    # ======================================================

    executive_summary = build_executive_summary(
        asset,
        score,
        classification,
        qualified_signal,
        trend,
        risk,
        recommendation,
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

        # --------------------------------------------------
        # CONFIABILIDADE
        # --------------------------------------------------

        "score_reliable":
            True,

        "reliable":
            True,

        "analysis_reliable":
            True,

        "status":
            "ANÁLISE CONFIÁVEL",

        "status_icon":
            "🟢",

        "status_message":
            (
                "Todos os indicadores necessários "
                "estão disponíveis e o Score foi "
                "calculado normalmente."
            ),

        "validation":
            validation,

        "score_validation":
            score_details.get(
                "validation",
                {},
            ),

        "missing_indicators":
            [],

        "invalid_indicators":
            [],

    }


# ==========================================================
# FUNÇÃO DE COMPATIBILIDADE
# ==========================================================

def get_analysis_status(
    result,
):
    """
    Retorna somente o status de confiabilidade
    da análise.
    """

    if not isinstance(
        result,
        dict,
    ):

        return {

            "reliable":
                False,

            "status":
                "INDISPONÍVEL",

            "icon":
                "🔴",

            "message":
                "Resultado da análise inválido.",

        }

    reliable = result.get(
        "analysis_reliable",
        result.get(
            "score_reliable",
            False,
        ),
    )

    if reliable:

        return {

            "reliable":
                True,

            "status":
                "CONFIÁVEL",

            "icon":
                "🟢",

            "message":
                "Análise calculada com dados válidos.",

        }

    return {

        "reliable":
            False,

        "status":
            "NÃO CONFIÁVEL",

        "icon":
            "🔴",

        "message":
            result.get(
                "status_message",
                "Dados insuficientes para análise.",
            ),

    }
