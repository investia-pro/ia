"""
InvestIA PRO
Motor de Análise Técnica, Fundamentalista e Integrada

Versão: v0.7
Fase: 3.0.3 - Score InvestIA Integrado
"""

from score import (
    calculate_score_details,
    calculate_fundamental_score_details,
    classify_score,
    classify_signal,
)

from config import (
    RSI_OVERSOLD,
    RSI_OVERBOUGHT,
)


# ==========================================================
# PESOS DO SCORE INTEGRADO
# ==========================================================

TECHNICAL_WEIGHT = 0.55

FUNDAMENTAL_WEIGHT = 0.45


# ==========================================================
# CONVERSÃO SEGURA
# ==========================================================

def safe_float(
    value,
    default=None,
):
    """
    Converte valores para float com segurança.
    """

    try:

        if value is None:
            return default

        if isinstance(
            value,
            bool,
        ):
            return default

        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return default


# ==========================================================
# LIMITAÇÃO DO SCORE
# ==========================================================

def clamp_score(
    score,
):
    """
    Mantém o Score entre 0 e 100.
    """

    score = safe_float(
        score,
        default=0,
    )

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
# VALIDAÇÃO DE DADOS TÉCNICOS
# ==========================================================

def validate_technical_data(
    data,
):
    """
    Verifica se existem os dados mínimos
    necessários para a análise técnica.
    """

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

        value = safe_float(
            data.get(
                field
            )
        )

        if value is None:
            return False

    return True


# ==========================================================
# NORMALIZAÇÃO DOS FUNDAMENTOS
# ==========================================================

def normalize_fundamentals(
    fundamentals,
):
    """
    Garante uma estrutura fundamentalista
    consistente para o motor de análise.
    """

    if not isinstance(
        fundamentals,
        dict,
    ):

        fundamentals = {}

    fields = [

        "company_name",

        "sector",

        "industry",

        "market_cap",

        "pe_ratio",

        "price_to_book",

        "dividend_yield",

        "roe",

        "profit_margin",

        "debt_to_equity",

        "total_revenue",

        "net_income",
    ]

    normalized = {}

    for field in fields:

        normalized[field] = fundamentals.get(
            field
        )

    return normalized


# ==========================================================
# DISPONIBILIDADE DOS FUNDAMENTOS
# ==========================================================

def get_fundamental_data_status(
    fundamentals,
):
    """
    Avalia a quantidade de indicadores
    fundamentalistas disponíveis.

    Os indicadores considerados para o
    Score Fundamentalista são:

        - P/L
        - P/VP
        - Dividend Yield
        - ROE
        - Margem de Lucro
        - Dívida/Patrimônio
    """

    fundamentals = normalize_fundamentals(
        fundamentals
    )

    score_fields = [

        "pe_ratio",

        "price_to_book",

        "dividend_yield",

        "roe",

        "profit_margin",

        "debt_to_equity",
    ]

    available = 0

    missing = []

    for field in score_fields:

        value = safe_float(
            fundamentals.get(
                field
            )
        )

        if value is None:

            missing.append(
                field
            )

        else:

            available += 1

    total = len(
        score_fields
    )

    completeness = (
        available / total
        if total > 0
        else 0
    )

    if available == 0:

        status = "Indisponível"

    elif completeness < 0.50:

        status = "Limitado"

    elif completeness < 1:

        status = "Parcial"

    else:

        status = "Completo"

    return {

        "available":
            available,

        "total":
            total,

        "missing":
            missing,

        "completeness":
            completeness,

        "status":
            status,
    }


# ==========================================================
# TENDÊNCIA TÉCNICA
# ==========================================================

def get_trend(
    technical_data,
):
    """
    Determina a tendência com base no preço,
    MA21 e MA200.
    """

    if not validate_technical_data(
        technical_data
    ):

        return "Indisponível"

    price = safe_float(
        technical_data.get(
            "price"
        )
    )

    ma21 = safe_float(
        technical_data.get(
            "ma21"
        )
    )

    ma200 = safe_float(
        technical_data.get(
            "ma200"
        )
    )

    # Tendência forte de alta
    if (
        price > ma21
        and ma21 > ma200
    ):

        return "Alta Forte"

    # Alta
    if (
        price > ma21
        and price > ma200
    ):

        return "Alta"

    # Tendência forte de baixa
    if (
        price < ma21
        and ma21 < ma200
    ):

        return "Baixa Forte"

    # Baixa
    if (
        price < ma21
        and price < ma200
    ):

        return "Baixa"

    return "Neutra"


# ==========================================================
# STATUS DO RSI
# ==========================================================

def get_rsi_status(
    rsi,
):
    """
    Classifica a situação do RSI.
    """

    rsi = safe_float(
        rsi
    )

    if rsi is None:

        return "Indisponível"

    if rsi <= RSI_OVERSOLD:

        return "Sobrevendido"

    if rsi >= RSI_OVERBOUGHT:

        return "Sobrecomprado"

    if rsi >= 60:

        return "Positivo"

    if rsi <= 40:

        return "Negativo"

    return "Neutro"


# ==========================================================
# QUALIFICAÇÃO DO SINAL
# ==========================================================

def get_qualified_signal(
    technical_score,
    fundamental_score,
    fundamental_status,
):
    """
    Qualifica o sinal considerando a combinação
    entre análise técnica e fundamentalista.
    """

    technical_signal = classify_signal(
        technical_score
    )

    # ------------------------------------------------------
    # FUNDAMENTOS INDISPONÍVEIS
    # ------------------------------------------------------

    if fundamental_status == "Indisponível":

        if technical_signal == "POSITIVO":

            return (
                "POSITIVO TÉCNICO"
            )

        if technical_signal == "NEGATIVO":

            return (
                "NEGATIVO TÉCNICO"
            )

        return (
            "NEUTRO TÉCNICO"
        )

    fundamental_signal = classify_signal(
        fundamental_score
    )

    # ------------------------------------------------------
    # CONVERGÊNCIA POSITIVA
    # ------------------------------------------------------

    if (
        technical_signal == "POSITIVO"
        and fundamental_signal == "POSITIVO"
    ):

        return (
            "POSITIVO CONFIRMADO"
        )

    # ------------------------------------------------------
    # CONVERGÊNCIA NEGATIVA
    # ------------------------------------------------------

    if (
        technical_signal == "NEGATIVO"
        and fundamental_signal == "NEGATIVO"
    ):

        return (
            "NEGATIVO CONFIRMADO"
        )

    # ------------------------------------------------------
    # DIVERGÊNCIA
    # ------------------------------------------------------

    if (
        technical_signal == "POSITIVO"
        and fundamental_signal == "NEGATIVO"
    ):

        return (
            "DIVERGÊNCIA POSITIVA"
        )

    if (
        technical_signal == "NEGATIVO"
        and fundamental_signal == "POSITIVO"
    ):

        return (
            "DIVERGÊNCIA NEGATIVA"
        )

    # ------------------------------------------------------
    # FUNDAMENTOS FORTES
    # ------------------------------------------------------

    if (
        technical_signal == "NEUTRO"
        and fundamental_signal == "POSITIVO"
    ):

        return (
            "POSITIVO FUNDAMENTAL"
        )

    # ------------------------------------------------------
    # FUNDAMENTOS FRACOS
    # ------------------------------------------------------

    if (
        technical_signal == "NEUTRO"
        and fundamental_signal == "NEGATIVO"
    ):

        return (
            "NEGATIVO FUNDAMENTAL"
        )

    # ------------------------------------------------------
    # TÉCNICO POSITIVO + FUNDAMENTAL NEUTRO
    # ------------------------------------------------------

    if technical_signal == "POSITIVO":

        return (
            "POSITIVO COM MODERAÇÃO"
        )

    # ------------------------------------------------------
    # TÉCNICO NEGATIVO + FUNDAMENTAL NEUTRO
    # ------------------------------------------------------

    if technical_signal == "NEGATIVO":

        return (
            "NEGATIVO COM MODERAÇÃO"
        )

    return "NEUTRO"


# ==========================================================
# NÍVEL DO SINAL
# ==========================================================

def get_signal_level(
    integrated_score,
):
    """
    Define o nível operacional do sinal.
    """

    integrated_score = clamp_score(
        integrated_score
    )

    if integrated_score >= 80:

        return "Muito Forte"

    if integrated_score >= 65:

        return "Forte"

    if integrated_score >= 55:

        return "Moderado"

    if integrated_score >= 45:

        return "Aguardar"

    if integrated_score >= 35:

        return "Fraco"

    return "Muito Fraco"


# ==========================================================
# ÍCONE DO SINAL
# ==========================================================

def get_signal_icon(
    signal,
):
    """
    Retorna o ícone visual do sinal.
    """

    signal = str(
        signal
    ).upper()

    if "POSITIVO" in signal:

        return "🟢"

    if "NEGATIVO" in signal:

        return "🔴"

    if "DIVERGÊNCIA" in signal:

        return "🟠"

    return "🟡"


# ==========================================================
# SCORE INTEGRADO
# ==========================================================

def calculate_integrated_score(
    technical_score,
    fundamental_score=None,
    fundamental_status="Indisponível",
):
    """
    Calcula o Score Integrado InvestIA.

    Regra padrão:

        55% Técnico
        45% Fundamentalista

    Quando os fundamentos não estiverem
    disponíveis, utiliza 100% do Score Técnico.

    Quando os dados forem limitados ou parciais,
    o Score Fundamentalista continua sendo usado,
    mas sua disponibilidade será informada no
    resultado da análise.
    """

    technical_score = clamp_score(
        technical_score
    )

    if fundamental_status == "Indisponível":

        return {

            "score":
                technical_score,

            "technical_weight":
                1.00,

            "fundamental_weight":
                0.00,

            "method":
                "Técnico",
        }

    fundamental_score = safe_float(
        fundamental_score
    )

    if fundamental_score is None:

        return {

            "score":
                technical_score,

            "technical_weight":
                1.00,

            "fundamental_weight":
                0.00,

            "method":
                "Técnico",
        }

    integrated_score = (

        technical_score
        * TECHNICAL_WEIGHT

        +

        fundamental_score
        * FUNDAMENTAL_WEIGHT
    )

    return {

        "score":
            clamp_score(
                integrated_score
            ),

        "technical_weight":
            TECHNICAL_WEIGHT,

        "fundamental_weight":
            FUNDAMENTAL_WEIGHT,

        "method":
            "Técnico + Fundamentalista",
    }


# ==========================================================
# GESTÃO DE RISCO
# ==========================================================

def get_risk(
    integrated_score,
    volatility=None,
    fundamental_status="Indisponível",
):
    """
    Define o nível geral de risco.

    Combina:

        - Score Integrado
        - Volatilidade
        - Disponibilidade dos fundamentos
    """

    score = clamp_score(
        integrated_score
    )

    volatility = safe_float(
        volatility
    )

    # ------------------------------------------------------
    # RISCO BASE
    # ------------------------------------------------------

    if score >= 75:

        risk = "Baixo"

    elif score >= 55:

        risk = "Moderado"

    elif score >= 35:

        risk = "Alto"

    else:

        risk = "Muito Alto"

    # ------------------------------------------------------
    # AJUSTE POR VOLATILIDADE
    # ------------------------------------------------------

    if volatility is not None:

        if volatility >= 0.04:

            if risk == "Baixo":
                risk = "Moderado"

            elif risk == "Moderado":
                risk = "Alto"

            elif risk == "Alto":
                risk = "Muito Alto"

    # ------------------------------------------------------
    # AJUSTE POR FUNDAMENTOS LIMITADOS
    # ------------------------------------------------------

    if fundamental_status == "Indisponível":

        if risk == "Baixo":
            risk = "Moderado"

    return risk


# ==========================================================
# RECOMENDAÇÃO INTEGRADA
# ==========================================================

def get_recommendation(
    integrated_score,
    qualified_signal,
    risk,
):
    """
    Define a recomendação final do InvestIA.
    """

    score = clamp_score(
        integrated_score
    )

    signal = str(
        qualified_signal
    ).upper()

    risk = str(
        risk
    ).upper()

    # ------------------------------------------------------
    # COMPRA FORTE
    # ------------------------------------------------------

    if (
        score >= 80
        and "POSITIVO CONFIRMADO" in signal
        and risk in [
            "BAIXO",
            "MODERADO",
        ]
    ):

        return "Compra Forte"

    # ------------------------------------------------------
    # COMPRA
    # ------------------------------------------------------

    if (
        score >= 65
        and "POSITIVO" in signal
    ):

        return "Compra"

    # ------------------------------------------------------
    # COMPRA GRADUAL
    # ------------------------------------------------------

    if score >= 55:

        return "Compra Gradual"

    # ------------------------------------------------------
    # VENDA
    # ------------------------------------------------------

    if (
        score <= 35
        and "NEGATIVO" in signal
    ):

        return "Venda"

    # ------------------------------------------------------
    # REDUÇÃO
    # ------------------------------------------------------

    if score <= 45:

        return "Reduzir Exposição"

    return "Aguardar"


# ==========================================================
# JUSTIFICATIVAS TÉCNICAS
# ==========================================================

def get_technical_reasons(
    technical_breakdown,
):
    """
    Extrai as justificativas da análise técnica.
    """

    reasons = []

    if not isinstance(
        technical_breakdown,
        dict,
    ):

        return reasons

    labels = {

        "ma21":
            "MA21",

        "ma200":
            "MA200",

        "rsi":
            "RSI",
    }

    for key, label in labels.items():

        data = technical_breakdown.get(
            key,
            {}
        )

        if not isinstance(
            data,
            dict,
        ):
            continue

        reason = data.get(
            "reason"
        )

        if reason:

            reasons.append(
                f"{label}: {reason}"
            )

    return reasons


# ==========================================================
# JUSTIFICATIVAS FUNDAMENTALISTAS
# ==========================================================

def get_fundamental_reasons(
    fundamental_breakdown,
):
    """
    Extrai as justificativas da análise
    fundamentalista.
    """

    reasons = []

    if not isinstance(
        fundamental_breakdown,
        dict,
    ):

        return reasons

    labels = {

        "pe_ratio":
            "P/L",

        "price_to_book":
            "P/VP",

        "dividend_yield":
            "Dividend Yield",

        "roe":
            "ROE",

        "profit_margin":
            "Margem de Lucro",

        "debt_to_equity":
            "Endividamento",
    }

    for key, label in labels.items():

        data = fundamental_breakdown.get(
            key,
            {}
        )

        if not isinstance(
            data,
            dict,
        ):
            continue

        reason = data.get(
            "reason"
        )

        signal = data.get(
            "signal"
        )

        if reason:

            if signal:

                reasons.append(
                    f"{label}: {reason} "
                    f"({signal})"
                )

            else:

                reasons.append(
                    f"{label}: {reason}"
                )

    return reasons


# ==========================================================
# RESUMO EXECUTIVO
# ==========================================================

def build_executive_summary(
    asset,
    integrated_score,
    technical_score,
    fundamental_score,
    fundamental_status,
    trend,
    recommendation,
    risk,
    qualified_signal,
):
    """
    Gera o resumo executivo da análise integrada.
    """

    asset_name = (
        str(asset).upper()
        if asset
        else "ATIVO"
    )

    integrated_score = clamp_score(
        integrated_score
    )

    technical_score = clamp_score(
        technical_score
    )

    parts = [

        f"{asset_name} apresenta "
        f"Score InvestIA Integrado de "
        f"{integrated_score}/100.",

        f"O Score Técnico é "
        f"{technical_score}/100.",

        f"A tendência atual é "
        f"{trend}.",
    ]

    if (
        fundamental_status
        != "Indisponível"
        and fundamental_score
        is not None
    ):

        fundamental_score = clamp_score(
            fundamental_score
        )

        parts.append(

            f"O Score Fundamentalista é "
            f"{fundamental_score}/100 "
            f"com cobertura de dados "
            f"{fundamental_status.lower()}."
        )

    else:

        parts.append(

            "Os dados fundamentalistas não estão "
            "disponíveis no momento; a decisão "
            "está baseada principalmente na "
            "análise técnica."
        )

    parts.append(

        f"O sinal integrado é "
        f"{qualified_signal}."
    )

    parts.append(

        f"A recomendação atual é "
        f"{recommendation}, "
        f"com nível de risco {risk.lower()}."
    )

    return " ".join(
        parts
    )


# ==========================================================
# ANÁLISE PRINCIPAL
# ==========================================================

def analyze_asset(
    data,
    asset=None,
):
    """
    Executa a análise completa do InvestIA PRO.

    Parâmetros:

        data:
            Dicionário contendo dados técnicos
            e, opcionalmente, fundamentos.

        asset:
            Código do ativo.

    Estrutura esperada:

        {
            "price": ...,
            "ma21": ...,
            "ma200": ...,
            "rsi": ...,
            "volatility": ...,
            "fundamentals": {...}
        }
    """

    if not isinstance(
        data,
        dict,
    ):

        raise ValueError(
            "Os dados da análise devem ser "
            "fornecidos em formato de dicionário."
        )

    # ======================================================
    # DADOS TÉCNICOS
    # ======================================================

    technical_data = {

        "price":
            data.get(
                "price"
            ),

        "ma21":
            data.get(
                "ma21"
            ),

        "ma200":
            data.get(
                "ma200"
            ),

        "rsi":
            data.get(
                "rsi"
            ),
    }

    if not validate_technical_data(
        technical_data
    ):

        raise ValueError(
            "Dados técnicos insuficientes "
            "para realizar a análise."
        )

    volatility = safe_float(
        data.get(
            "volatility"
        )
    )

    # ======================================================
    # SCORE TÉCNICO
    # ======================================================

    technical_result = calculate_score_details(
        technical_data
    )

    technical_score = technical_result.get(
        "score",
        0,
    )

    technical_classification = (
        technical_result.get(
            "classification",
            "NEUTRO",
        )
    )

    technical_signal = technical_result.get(
        "signal",
        "NEUTRO",
    )

    technical_breakdown = technical_result.get(
        "breakdown",
        {},
    )

    # ======================================================
    # FUNDAMENTOS
    # ======================================================

    fundamentals = normalize_fundamentals(
        data.get(
            "fundamentals",
            {}
        )
    )

    fundamental_data_status = (
        get_fundamental_data_status(
            fundamentals
        )
    )

    fundamental_status = (
        fundamental_data_status.get(
            "status",
            "Indisponível",
        )
    )

    fundamental_score = None

    fundamental_classification = (
        "Indisponível"
    )

    fundamental_signal = (
        "Indisponível"
    )

    fundamental_breakdown = {}

    # ======================================================
    # SCORE FUNDAMENTALISTA
    # ======================================================

    if fundamental_status != "Indisponível":

        try:

            fundamental_result = (
                calculate_fundamental_score_details(
                    fundamentals
                )
            )

            fundamental_score = (
                fundamental_result.get(
                    "score"
                )
            )

            fundamental_classification = (
                fundamental_result.get(
                    "classification",
                    "NEUTRO",
                )
            )

            fundamental_signal = (
                fundamental_result.get(
                    "signal",
                    "NEUTRO",
                )
            )

            fundamental_breakdown = (
                fundamental_result.get(
                    "breakdown",
                    {}
                )
            )

        except Exception:

            fundamental_status = (
                "Indisponível"
            )

            fundamental_score = None

            fundamental_breakdown = {}

    # ======================================================
    # SCORE INTEGRADO
    # ======================================================

    integrated_result = (
        calculate_integrated_score(
            technical_score=
                technical_score,

            fundamental_score=
                fundamental_score,

            fundamental_status=
                fundamental_status,
        )
    )

    integrated_score = (
        integrated_result.get(
            "score",
            technical_score,
        )
    )

    integrated_classification = (
        classify_score(
            integrated_score
        )
    )

    integrated_signal = (
        classify_signal(
            integrated_score
        )
    )

    # ======================================================
    # TENDÊNCIA
    # ======================================================

    trend = get_trend(
        technical_data
    )

    # ======================================================
    # RSI
    # ======================================================

    rsi_status = get_rsi_status(
        technical_data.get(
            "rsi"
        )
    )

    # ======================================================
    # SINAL QUALIFICADO
    # ======================================================

    qualified_signal = (
        get_qualified_signal(
            technical_score=
                technical_score,

            fundamental_score=
                fundamental_score,

            fundamental_status=
                fundamental_status,
        )
    )

    # ======================================================
    # NÍVEL DO SINAL
    # ======================================================

    signal_level = get_signal_level(
        integrated_score
    )

    signal_icon = get_signal_icon(
        qualified_signal
    )

    # ======================================================
    # RISCO
    # ======================================================

    risk = get_risk(
        integrated_score=
            integrated_score,

        volatility=
            volatility,

        fundamental_status=
            fundamental_status,
    )

    # ======================================================
    # RECOMENDAÇÃO
    # ======================================================

    recommendation = get_recommendation(
        integrated_score=
            integrated_score,

        qualified_signal=
            qualified_signal,

        risk=
            risk,
    )

    # ======================================================
    # JUSTIFICATIVAS
    # ======================================================

    technical_reasons = (
        get_technical_reasons(
            technical_breakdown
        )
    )

    fundamental_reasons = (
        get_fundamental_reasons(
            fundamental_breakdown
        )
    )

    reasons = (
        technical_reasons
        + fundamental_reasons
    )

    # ======================================================
    # RESUMO EXECUTIVO
    # ======================================================

    executive_summary = (
        build_executive_summary(
            asset=
                asset,

            integrated_score=
                integrated_score,

            technical_score=
                technical_score,

            fundamental_score=
                fundamental_score,

            fundamental_status=
                fundamental_status,

            trend=
                trend,

            recommendation=
                recommendation,

            risk=
                risk,

            qualified_signal=
                qualified_signal,
        )
    )

    # ======================================================
    # BREAKDOWN INTEGRADO
    # ======================================================

    integrated_breakdown = {

        "technical": {

            "score":
                technical_score,

            "classification":
                technical_classification,

            "signal":
                technical_signal,

            "weight":
                integrated_result.get(
                    "technical_weight",
                    1.00,
                ),

            "breakdown":
                technical_breakdown,
        },

        "fundamental": {

            "score":
                fundamental_score,

            "classification":
                fundamental_classification,

            "signal":
                fundamental_signal,

            "weight":
                integrated_result.get(
                    "fundamental_weight",
                    0.00,
                ),

            "status":
                fundamental_status,

            "available":
                fundamental_data_status.get(
                    "available",
                    0,
                ),

            "total":
                fundamental_data_status.get(
                    "total",
                    0,
                ),

            "completeness":
                fundamental_data_status.get(
                    "completeness",
                    0,
                ),

            "missing":
                fundamental_data_status.get(
                    "missing",
                    []
                ),

            "breakdown":
                fundamental_breakdown,
        },

        "integrated": {

            "score":
                integrated_score,

            "classification":
                integrated_classification,

            "signal":
                integrated_signal,

            "method":
                integrated_result.get(
                    "method",
                    "Técnico",
                ),
        },
    }

    # ======================================================
    # RETORNO FINAL
    # ======================================================

    return {

        # --------------------------------------------------
        # SCORE PRINCIPAL
        # --------------------------------------------------

        "score":
            integrated_score,

        "classification":
            integrated_classification,

        "signal":
            integrated_signal,

        "qualified_signal":
            qualified_signal,

        "signal_level":
            signal_level,

        "signal_icon":
            signal_icon,

        # --------------------------------------------------
        # ANÁLISE
        # --------------------------------------------------

        "trend":
            trend,

        "tendencia":
            trend,

        "recommendation":
            recommendation,

        "recomendacao":
            recommendation,

        "risk":
            risk,

        "risco":
            risk,

        "rsi_status":
            rsi_status,

        # --------------------------------------------------
        # SCORES
        # --------------------------------------------------

        "technical_score":
            technical_score,

        "fundamental_score":
            fundamental_score,

        "integrated_score":
            integrated_score,

        # --------------------------------------------------
        # CLASSIFICAÇÕES
        # --------------------------------------------------

        "technical_classification":
            technical_classification,

        "fundamental_classification":
            fundamental_classification,

        "integrated_classification":
            integrated_classification,

        # --------------------------------------------------
        # SINAIS
        # --------------------------------------------------

        "technical_signal":
            technical_signal,

        "fundamental_signal":
            fundamental_signal,

        "integrated_signal":
            integrated_signal,

        # --------------------------------------------------
        # FUNDAMENTOS
        # --------------------------------------------------

        "fundamental_status":
            fundamental_status,

        "fundamental_completeness":
            fundamental_data_status.get(
                "completeness",
                0,
            ),

        # --------------------------------------------------
        # EXPLICAÇÃO
        # --------------------------------------------------

        "reasons":
            reasons,

        "justificativas":
            reasons,

        "technical_reasons":
            technical_reasons,

        "fundamental_reasons":
            fundamental_reasons,

        "breakdown":
            technical_breakdown,

        "technical_breakdown":
            technical_breakdown,

        "fundamental_breakdown":
            fundamental_breakdown,

        "integrated_breakdown":
            integrated_breakdown,

        # --------------------------------------------------
        # RESUMO
        # --------------------------------------------------

        "executive_summary":
            executive_summary,

        "asset":
            asset,
    }
