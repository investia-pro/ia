"""
InvestIA PRO
Motor de Análise Integrada

Versão: v0.7
Fase: 3.0.4 - Consenso e Confiança da Análise

Responsabilidades:
- Interpretar indicadores técnicos
- Integrar Score Técnico e Fundamentalista
- Calcular divergência entre os modelos
- Determinar consenso
- Calcular confiança da análise
- Ajustar recomendação final
- Gerar resumo executivo
"""

from score import (
    calculate_score_details,
    calculate_fundamental_score_details,
)


# ==========================================================
# FUNÇÕES AUXILIARES
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

        score = 50

    return max(
        0,
        min(
            100,
            round(score),
        ),
    )


def safe_number(
    value,
    default=None,
):
    """
    Converte valores para float com segurança.
    """

    if value is None:

        return default

    try:

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return default


def get_dict_value(
    data,
    *keys,
    default=None,
):
    """
    Obtém valores de um dicionário aceitando
    múltiplos nomes possíveis para a mesma chave.
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


# ==========================================================
# CLASSIFICAÇÃO DO SCORE
# ==========================================================

def classify_score(score):
    """
    Classifica o Score de 0 a 100.
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
# CLASSIFICAÇÃO DO SINAL
# ==========================================================

def classify_signal(score):
    """
    Define o sinal principal do Score.
    """

    score = clamp_score(
        score
    )

    if score >= 65:
        return "POSITIVO"

    if score <= 35:
        return "NEGATIVO"

    return "NEUTRO"


# ==========================================================
# NÍVEL DO SINAL
# ==========================================================

def get_signal_level(
    score,
):
    """
    Define a intensidade do sinal.
    """

    score = clamp_score(
        score
    )

    if score >= 85:

        return {
            "level": "Muito Forte",
            "icon": "🟢",
        }

    if score >= 65:

        return {
            "level": "Positivo",
            "icon": "🟢",
        }

    if score >= 55:

        return {
            "level": "Levemente Positivo",
            "icon": "🟡",
        }

    if score >= 45:

        return {
            "level": "Neutro",
            "icon": "🟡",
        }

    if score >= 35:

        return {
            "level": "Levemente Negativo",
            "icon": "🟠",
        }

    return {
        "level": "Negativo",
        "icon": "🔴",
    }


# ==========================================================
# TENDÊNCIA TÉCNICA
# ==========================================================

def analyze_trend(
    data,
):
    """
    Analisa a tendência utilizando
    preço, MA21 e MA200.
    """

    price = safe_number(
        get_dict_value(
            data,
            "price",
        )
    )

    ma21 = safe_number(
        get_dict_value(
            data,
            "ma21",
        )
    )

    ma200 = safe_number(
        get_dict_value(
            data,
            "ma200",
        )
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
        and ma21 > ma200
    ):

        return "Alta Forte"

    if (
        price > ma21
        and price > ma200
    ):

        return "Alta"

    if (
        price < ma21
        and price < ma200
        and ma21 < ma200
    ):

        return "Baixa Forte"

    if (
        price < ma21
        and price < ma200
    ):

        return "Baixa"

    return "Neutra"


# ==========================================================
# STATUS DO RSI
# ==========================================================

def analyze_rsi(
    rsi,
):
    """
    Interpreta o RSI.
    """

    rsi = safe_number(
        rsi
    )

    if rsi is None:

        return "Indisponível"

    if rsi <= 30:

        return "Sobrevendido"

    if rsi >= 70:

        return "Sobrecomprado"

    if rsi > 55:

        return "Positivo"

    if rsi < 45:

        return "Negativo"

    return "Neutro"


# ==========================================================
# ANÁLISE DO RISCO
# ==========================================================

def analyze_risk(
    volatility,
    divergence=0,
    fundamental_status=None,
):
    """
    Determina o nível de risco considerando:

    - Volatilidade
    - Divergência entre os Scores
    - Disponibilidade dos fundamentos
    """

    volatility = safe_number(
        volatility,
        default=0,
    )

    divergence = safe_number(
        divergence,
        default=0,
    )

    risk_points = 0

    # ------------------------------------------------------
    # VOLATILIDADE
    # ------------------------------------------------------

    if volatility >= 0.04:

        risk_points += 3

    elif volatility >= 0.025:

        risk_points += 2

    elif volatility >= 0.015:

        risk_points += 1

    # ------------------------------------------------------
    # DIVERGÊNCIA
    # ------------------------------------------------------

    if divergence >= 35:

        risk_points += 2

    elif divergence >= 20:

        risk_points += 1

    # ------------------------------------------------------
    # FUNDAMENTOS
    # ------------------------------------------------------

    if fundamental_status in (
        "Indisponível",
        "Insuficiente",
    ):

        risk_points += 1

    # ------------------------------------------------------
    # CLASSIFICAÇÃO
    # ------------------------------------------------------

    if risk_points >= 5:

        return "Alto"

    if risk_points >= 3:

        return "Moderado-Alto"

    if risk_points >= 1:

        return "Moderado"

    return "Baixo"


# ==========================================================
# CONSENSO ENTRE OS SCORES
# ==========================================================

def analyze_score_consensus(
    technical_score,
    fundamental_score,
):
    """
    Analisa o grau de concordância entre
    o Score Técnico e Fundamentalista.
    """

    technical_score = safe_number(
        technical_score
    )

    fundamental_score = safe_number(
        fundamental_score
    )

    # ------------------------------------------------------
    # SEM SCORE FUNDAMENTALISTA
    # ------------------------------------------------------

    if fundamental_score is None:

        return {

            "consensus": "NÃO AVALIADO",

            "divergence": None,

            "direction_agreement": False,

            "reason": (
                "Não há dados fundamentalistas "
                "suficientes para comparar os Scores."
            ),
        }

    # ------------------------------------------------------
    # DIVERGÊNCIA NUMÉRICA
    # ------------------------------------------------------

    divergence = abs(
        technical_score
        - fundamental_score
    )

    technical_signal = classify_signal(
        technical_score
    )

    fundamental_signal = classify_signal(
        fundamental_score
    )

    direction_agreement = (
        technical_signal
        == fundamental_signal
    )

    # ------------------------------------------------------
    # FORTE CONSENSO
    # ------------------------------------------------------

    if (
        direction_agreement
        and divergence <= 10
    ):

        consensus = "FORTE"

        reason = (
            "Os Scores Técnico e Fundamentalista "
            "apresentam forte concordância."
        )

    # ------------------------------------------------------
    # CONSENSO MODERADO
    # ------------------------------------------------------

    elif (
        direction_agreement
        and divergence <= 20
    ):

        consensus = "MODERADO"

        reason = (
            "Os modelos apontam para a mesma direção, "
            "mas existe diferença relevante na intensidade."
        )

    # ------------------------------------------------------
    # CONSENSO FRACO
    # ------------------------------------------------------

    elif (
        direction_agreement
        and divergence <= 30
    ):

        consensus = "FRACO"

        reason = (
            "Os modelos possuem a mesma direção geral, "
            "porém apresentam divergência elevada."
        )

    # ------------------------------------------------------
    # DIVERGÊNCIA
    # ------------------------------------------------------

    else:

        consensus = "DIVERGENTE"

        reason = (
            "A análise Técnica e Fundamentalista "
            "não apresentam convergência suficiente."
        )

    return {

        "consensus": consensus,

        "divergence": round(
            divergence,
            2,
        ),

        "direction_agreement":
            direction_agreement,

        "technical_signal":
            technical_signal,

        "fundamental_signal":
            fundamental_signal,

        "reason":
            reason,
    }


# ==========================================================
# CONFIANÇA DA ANÁLISE
# ==========================================================

def analyze_confidence(
    consensus_data,
    fundamental_status,
    fundamental_completeness,
):
    """
    Determina a confiança da análise.

    Critérios:

    - Disponibilidade dos fundamentos
    - Cobertura dos dados
    - Consenso entre os modelos
    """

    consensus = get_dict_value(
        consensus_data,
        "consensus",
        default="NÃO AVALIADO",
    )

    completeness = safe_number(
        fundamental_completeness,
        default=0,
    )

    # ------------------------------------------------------
    # SEM FUNDAMENTOS
    # ------------------------------------------------------

    if fundamental_status in (
        "Indisponível",
        "Insuficiente",
    ):

        return {

            "confidence": "MÉDIA",

            "confidence_score": 50,

            "reason": (
                "A análise possui confiança moderada "
                "porque está baseada predominantemente "
                "em indicadores técnicos."
            ),
        }

    # ------------------------------------------------------
    # FORTE CONSENSO
    # ------------------------------------------------------

    if (
        consensus == "FORTE"
        and completeness >= 0.80
    ):

        return {

            "confidence": "ALTA",

            "confidence_score": 90,

            "reason": (
                "Os modelos técnico e fundamentalista "
                "apresentam forte convergência e boa "
                "cobertura de dados."
            ),
        }

    # ------------------------------------------------------
    # CONSENSO MODERADO
    # ------------------------------------------------------

    if (
        consensus == "MODERADO"
        and completeness >= 0.60
    ):

        return {

            "confidence": "MÉDIA-ALTA",

            "confidence_score": 75,

            "reason": (
                "Existe concordância entre os modelos "
                "e cobertura adequada dos fundamentos."
            ),
        }

    # ------------------------------------------------------
    # CONSENSO FRACO
    # ------------------------------------------------------

    if consensus == "FRACO":

        return {

            "confidence": "MÉDIA",

            "confidence_score": 60,

            "reason": (
                "Os modelos apontam para a mesma direção, "
                "mas a diferença entre os Scores reduz "
                "a confiança da conclusão."
            ),
        }

    # ------------------------------------------------------
    # DIVERGÊNCIA
    # ------------------------------------------------------

    if consensus == "DIVERGENTE":

        return {

            "confidence": "BAIXA",

            "confidence_score": 35,

            "reason": (
                "Existe divergência significativa entre "
                "a análise Técnica e Fundamentalista."
            ),
        }

    # ------------------------------------------------------
    # COBERTURA INCOMPLETA
    # ------------------------------------------------------

    return {

        "confidence": "MÉDIA",

        "confidence_score": 55,

        "reason": (
            "A análise possui cobertura parcial dos "
            "dados fundamentalistas."
        ),
    }


# ==========================================================
# RECOMENDAÇÃO BASE
# ==========================================================

def get_base_recommendation(
    score,
):
    """
    Define a recomendação base pelo Score.
    """

    score = clamp_score(
        score
    )

    if score >= 80:

        return "COMPRA FORTE"

    if score >= 65:

        return "COMPRA"

    if score >= 55:

        return "COMPRA COM CAUTELA"

    if score >= 45:

        return "AGUARDAR"

    if score >= 35:

        return "REDUZIR EXPOSIÇÃO"

    return "VENDA"


# ==========================================================
# AJUSTE DA RECOMENDAÇÃO
# ==========================================================

def adjust_recommendation(
    base_recommendation,
    consensus,
    confidence,
):
    """
    Ajusta a recomendação final considerando
    consenso e confiança da análise.
    """

    recommendation = (
        str(base_recommendation)
        .strip()
        .upper()
    )

    # ------------------------------------------------------
    # BAIXA CONFIANÇA
    # ------------------------------------------------------

    if confidence == "BAIXA":

        if recommendation in (
            "COMPRA FORTE",
            "COMPRA",
        ):

            return "AGUARDAR CONFIRMAÇÃO"

        return "CAUTELA"

    # ------------------------------------------------------
    # DIVERGÊNCIA
    # ------------------------------------------------------

    if consensus == "DIVERGENTE":

        if recommendation in (
            "COMPRA FORTE",
            "COMPRA",
            "COMPRA COM CAUTELA",
        ):

            return "AGUARDAR CONFIRMAÇÃO"

    # ------------------------------------------------------
    # CONSENSO FRACO
    # ------------------------------------------------------

    if (
        consensus == "FRACO"
        and recommendation == "COMPRA FORTE"
    ):

        return "COMPRA COM CAUTELA"

    return recommendation


# ==========================================================
# INTEGRAÇÃO DOS SCORES
# ==========================================================

def calculate_integrated_score(
    technical_score,
    fundamental_score=None,
    fundamental_completeness=0,
):
    """
    Calcula o Score Integrado.

    Regras:

    Com fundamentos confiáveis:
        55% Técnico
        45% Fundamentalista

    Com cobertura parcial:
        Peso Fundamentalista reduzido

    Sem fundamentos:
        100% Técnico
    """

    technical_score = clamp_score(
        technical_score
    )

    fundamental_score = safe_number(
        fundamental_score
    )

    completeness = safe_number(
        fundamental_completeness,
        default=0,
    )

    completeness = max(
        0,
        min(
            1,
            completeness,
        ),
    )

    # ------------------------------------------------------
    # SEM FUNDAMENTOS
    # ------------------------------------------------------

    if fundamental_score is None:

        return {

            "score":
                technical_score,

            "technical_weight":
                1.0,

            "fundamental_weight":
                0.0,

            "method":
                "Score Técnico - Fundamentos indisponíveis",
        }

    # ------------------------------------------------------
    # COBERTURA COMPLETA
    # ------------------------------------------------------

    if completeness >= 0.80:

        technical_weight = 0.55

        fundamental_weight = 0.45

        method = (
            "Score Integrado Completo"
        )

    # ------------------------------------------------------
    # COBERTURA PARCIAL
    # ------------------------------------------------------

    elif completeness >= 0.50:

        fundamental_weight = (
            0.45
            * completeness
        )

        technical_weight = (
            1
            - fundamental_weight
        )

        method = (
            "Score Integrado com Cobertura Parcial"
        )

    # ------------------------------------------------------
    # COBERTURA INSUFICIENTE
    # ------------------------------------------------------

    else:

        technical_weight = 1.0

        fundamental_weight = 0.0

        method = (
            "Score Técnico - Cobertura Fundamentalista Insuficiente"
        )

    integrated_score = (
        technical_score
        * technical_weight
        + fundamental_score
        * fundamental_weight
    )

    return {

        "score":
            clamp_score(
                integrated_score
            ),

        "technical_weight":
            technical_weight,

        "fundamental_weight":
            fundamental_weight,

        "method":
            method,
    }


# ==========================================================
# STATUS DOS FUNDAMENTOS
# ==========================================================

def get_fundamental_status(
    fundamentals,
    fundamental_result,
):
    """
    Define o status dos dados fundamentalistas.
    """

    if not isinstance(
        fundamentals,
        dict,
    ) or not fundamentals:

        return "Indisponível"

    fundamental_score = get_dict_value(
        fundamental_result,
        "score",
        default=None,
    )

    if fundamental_score is None:

        return "Insuficiente"

    completeness = get_dict_value(
        fundamental_result,
        "completeness",
        "coverage",
        default=0,
    )

    completeness = safe_number(
        completeness,
        default=0,
    )

    if completeness >= 0.80:

        return "Completo"

    if completeness >= 0.50:

        return "Parcial"

    return "Insuficiente"


# ==========================================================
# JUSTIFICATIVAS
# ==========================================================

def build_reasons(
    data,
    trend,
    rsi_status,
    consensus_data,
    confidence_data,
    fundamental_status,
):
    """
    Monta as justificativas da análise.
    """

    reasons = []

    # ------------------------------------------------------
    # TENDÊNCIA
    # ------------------------------------------------------

    reasons.append(
        f"Tendência técnica identificada: {trend}."
    )

    # ------------------------------------------------------
    # RSI
    # ------------------------------------------------------

    reasons.append(
        f"RSI em condição: {rsi_status}."
    )

    # ------------------------------------------------------
    # FUNDAMENTOS
    # ------------------------------------------------------

    reasons.append(
        f"Status dos dados fundamentalistas: "
        f"{fundamental_status}."
    )

    # ------------------------------------------------------
    # CONSENSO
    # ------------------------------------------------------

    consensus_reason = get_dict_value(
        consensus_data,
        "reason",
        default=None,
    )

    if consensus_reason:

        reasons.append(
            consensus_reason
        )

    # ------------------------------------------------------
    # CONFIANÇA
    # ------------------------------------------------------

    confidence_reason = get_dict_value(
        confidence_data,
        "reason",
        default=None,
    )

    if confidence_reason:

        reasons.append(
            confidence_reason
        )

    return reasons


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
    consensus,
    confidence,
):
    """
    Gera o resumo executivo da análise.
    """

    technical_text = (
        f"Score Técnico {technical_score}/100"
    )

    if fundamental_score is None:

        fundamental_text = (
            "os dados fundamentalistas "
            "não estão disponíveis"
        )

    else:

        fundamental_text = (
            f"Score Fundamentalista "
            f"{fundamental_score}/100"
        )

    return (
        f"O ativo {asset} apresenta "
        f"{technical_text} e "
        f"{fundamental_text}. "
        f"O Score Integrado é "
        f"{integrated_score}/100, "
        f"com tendência {trend}. "
        f"O consenso entre os modelos é "
        f"{consensus} e o nível de confiança "
        f"da análise é {confidence}. "
        f"A recomendação final é "
        f"{recommendation}. "
        f"O nível de risco identificado é "
        f"{risk}."
    )


# ==========================================================
# MOTOR PRINCIPAL
# ==========================================================

def analyze_asset(
    data,
    asset="ATIVO",
):
    """
    Executa a análise completa do ativo.

    Fluxo:

    1. Calcula Score Técnico
    2. Calcula Score Fundamentalista
    3. Calcula cobertura dos fundamentos
    4. Calcula Score Integrado
    5. Compara os dois Scores
    6. Mede consenso e divergência
    7. Calcula confiança
    8. Ajusta recomendação
    9. Calcula risco
    10. Gera resumo executivo
    """

    if not isinstance(
        data,
        dict,
    ):

        raise ValueError(
            "Os dados para análise devem ser um dicionário."
        )

    # ======================================================
    # DADOS TÉCNICOS
    # ======================================================

    technical_data = {

        "price":
            get_dict_value(
                data,
                "price",
            ),

        "ma21":
            get_dict_value(
                data,
                "ma21",
            ),

        "ma200":
            get_dict_value(
                data,
                "ma200",
            ),

        "rsi":
            get_dict_value(
                data,
                "rsi",
            ),
    }

    # ======================================================
    # SCORE TÉCNICO
    # ======================================================

    technical_result = calculate_score_details(
        technical_data
    )

    if not isinstance(
        technical_result,
        dict,
    ):

        raise ValueError(
            "O Score Técnico retornou um resultado inválido."
        )

    technical_score = get_dict_value(
        technical_result,
        "score",
        default=50,
    )

    technical_score = clamp_score(
        technical_score
    )

    technical_classification = get_dict_value(
        technical_result,
        "classification",
        default=classify_score(
            technical_score
        ),
    )

    technical_signal = get_dict_value(
        technical_result,
        "signal",
        default=classify_signal(
            technical_score
        ),
    )

    technical_breakdown = get_dict_value(
        technical_result,
        "breakdown",
        default={},
    )

    # ======================================================
    # DADOS FUNDAMENTALISTAS
    # ======================================================

    fundamentals = get_dict_value(
        data,
        "fundamentals",
        default={},
    )

    if not isinstance(
        fundamentals,
        dict,
    ):

        fundamentals = {}

    # ======================================================
    # SCORE FUNDAMENTALISTA
    # ======================================================

    fundamental_result = {}

    fundamental_score = None

    fundamental_classification = "Indisponível"

    fundamental_signal = "Indisponível"

    fundamental_breakdown = {}

    fundamental_completeness = 0

    if fundamentals:

        try:

            fundamental_result = (
                calculate_fundamental_score_details(
                    fundamentals
                )
            )

            if not isinstance(
                fundamental_result,
                dict,
            ):

                fundamental_result = {}

        except Exception:

            fundamental_result = {}

    if fundamental_result:

        fundamental_score = get_dict_value(
            fundamental_result,
            "score",
            default=None,
        )

        if fundamental_score is not None:

            fundamental_score = clamp_score(
                fundamental_score
            )

        fundamental_classification = (
            get_dict_value(
                fundamental_result,
                "classification",
                default=(
                    classify_score(
                        fundamental_score
                    )
                    if fundamental_score is not None
                    else "Indisponível"
                ),
            )
        )

        fundamental_signal = get_dict_value(
            fundamental_result,
            "signal",
            default=(
                classify_signal(
                    fundamental_score
                )
                if fundamental_score is not None
                else "Indisponível"
            ),
        )

        fundamental_breakdown = get_dict_value(
            fundamental_result,
            "breakdown",
            default={},
        )

        fundamental_completeness = (
            get_dict_value(
                fundamental_result,
                "completeness",
                "coverage",
                default=0,
            )
        )

    fundamental_completeness = safe_number(
        fundamental_completeness,
        default=0,
    )

    # ======================================================
    # STATUS FUNDAMENTALISTA
    # ======================================================

    fundamental_status = get_fundamental_status(
        fundamentals,
        fundamental_result,
    )

    # ======================================================
    # SCORE INTEGRADO
    # ======================================================

    integrated_data = calculate_integrated_score(
        technical_score=technical_score,
        fundamental_score=fundamental_score,
        fundamental_completeness=fundamental_completeness,
    )

    integrated_score = integrated_data[
        "score"
    ]

    integrated_classification = classify_score(
        integrated_score
    )

    integrated_signal = classify_signal(
        integrated_score
    )

    # ======================================================
    # CONSENSO
    # ======================================================

    consensus_data = analyze_score_consensus(
        technical_score,
        fundamental_score,
    )

    consensus = consensus_data[
        "consensus"
    ]

    divergence = consensus_data[
        "divergence"
    ]

    # ======================================================
    # CONFIANÇA
    # ======================================================

    confidence_data = analyze_confidence(
        consensus_data=consensus_data,
        fundamental_status=fundamental_status,
        fundamental_completeness=fundamental_completeness,
    )

    confidence = confidence_data[
        "confidence"
    ]

    confidence_score = confidence_data[
        "confidence_score"
    ]

    # ======================================================
    # TENDÊNCIA E RSI
    # ======================================================

    trend = analyze_trend(
        data
    )

    rsi_status = analyze_rsi(
        get_dict_value(
            data,
            "rsi",
        )
    )

    # ======================================================
    # RECOMENDAÇÃO
    # ======================================================

    base_recommendation = (
        get_base_recommendation(
            integrated_score
        )
    )

    recommendation = adjust_recommendation(
        base_recommendation=base_recommendation,
        consensus=consensus,
        confidence=confidence,
    )

    # ======================================================
    # SINAL QUALIFICADO
    # ======================================================

    if confidence == "BAIXA":

        qualified_signal = (
            f"{integrated_signal} "
            f"COM BAIXA CONFIANÇA"
        )

    elif consensus == "DIVERGENTE":

        qualified_signal = (
            f"{integrated_signal} "
            f"COM DIVERGÊNCIA"
        )

    else:

        qualified_signal = (
            integrated_signal
        )

    signal_data = get_signal_level(
        integrated_score
    )

    # ======================================================
    # RISCO
    # ======================================================

    risk = analyze_risk(
        volatility=get_dict_value(
            data,
            "volatility",
            default=0,
        ),
        divergence=(
            divergence
            if divergence is not None
            else 0
        ),
        fundamental_status=fundamental_status,
    )

    # ======================================================
    # JUSTIFICATIVAS
    # ======================================================

    reasons = build_reasons(
        data=data,
        trend=trend,
        rsi_status=rsi_status,
        consensus_data=consensus_data,
        confidence_data=confidence_data,
        fundamental_status=fundamental_status,
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
        consensus=consensus,
        confidence=confidence,
    )

    # ======================================================
    # BREAKDOWN INTEGRADO
    # ======================================================

    integrated_breakdown = {

        "technical": {

            "score":
                technical_score,

            "weight":
                integrated_data[
                    "technical_weight"
                ],
        },

        "fundamental": {

            "score":
                fundamental_score,

            "weight":
                integrated_data[
                    "fundamental_weight"
                ],

            "completeness":
                fundamental_completeness,

            "status":
                fundamental_status,
        },

        "integrated": {

            "score":
                integrated_score,

            "method":
                integrated_data[
                    "method"
                ],
        },

        "consensus": {

            "level":
                consensus,

            "divergence":
                divergence,

            "direction_agreement":
                consensus_data.get(
                    "direction_agreement",
                    False,
                ),

            "reason":
                consensus_data.get(
                    "reason",
                ),
        },

        "confidence": {

            "level":
                confidence,

            "score":
                confidence_score,

            "reason":
                confidence_data.get(
                    "reason",
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
            technical_breakdown,

        # --------------------------------------------------
        # SCORE FUNDAMENTALISTA
        # --------------------------------------------------

        "fundamental_score":
            fundamental_score,

        "fundamental_classification":
            fundamental_classification,

        "fundamental_signal":
            fundamental_signal,

        "fundamental_status":
            fundamental_status,

        "fundamental_completeness":
            fundamental_completeness,

        "fundamental_breakdown":
            fundamental_breakdown,

        # --------------------------------------------------
        # SCORE INTEGRADO
        # --------------------------------------------------

        "integrated_score":
            integrated_score,

        "integrated_classification":
            integrated_classification,

        "integrated_signal":
            integrated_signal,

        "integrated_breakdown":
            integrated_breakdown,

        # --------------------------------------------------
        # CONSENSO
        # --------------------------------------------------

        "consensus":
            consensus,

        "divergence":
            divergence,

        "consensus_reason":
            consensus_data.get(
                "reason",
            ),

        # --------------------------------------------------
        # CONFIANÇA
        # --------------------------------------------------

        "confidence":
            confidence,

        "confidence_score":
            confidence_score,

        "confidence_reason":
            confidence_data.get(
                "reason",
            ),

        # --------------------------------------------------
        # ANÁLISE
        # --------------------------------------------------

        "trend":
            trend,

        "tendencia":
            trend,

        "rsi_status":
            rsi_status,

        "recommendation":
            recommendation,

        "recomendacao":
            recommendation,

        "risk":
            risk,

        "risco":
            risk,

        # --------------------------------------------------
        # SINAL QUALIFICADO
        # --------------------------------------------------

        "qualified_signal":
            qualified_signal,

        "signal_level":
            signal_data[
                "level"
            ],

        "signal_icon":
            signal_data[
                "icon"
            ],

        # --------------------------------------------------
        # EXPLICABILIDADE
        # --------------------------------------------------

        "reasons":
            reasons,

        "justificativas":
            reasons,

        "executive_summary":
            executive_summary,

        # --------------------------------------------------
        # COMPATIBILIDADE
        # --------------------------------------------------

        "breakdown":
            technical_breakdown,
    }
