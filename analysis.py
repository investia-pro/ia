"""
InvestIA PRO
Motor de Análise

Versão: v0.6
Fase: 2.9.6 - Estabilidade e Validação de Dados
"""

from score import (
    calculate_score_details,
)

from utils import (
    is_valid_number,
    safe_float,
    validate_indicators,
    validate_analysis_values,
)


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def _safe_text(
    value,
    default="N/D",
):
    """
    Retorna texto seguro para exibição.
    """

    if value is None:
        return default

    text = str(value).strip()

    if not text:
        return default

    return text


def _safe_list(
    value,
):
    """
    Garante que o retorno seja uma lista.
    """

    if value is None:
        return []

    if isinstance(
        value,
        list,
    ):
        return value

    return [value]


def _get_breakdown_item(
    breakdown,
    key,
):
    """
    Obtém um componente do breakdown com segurança.
    """

    if not isinstance(
        breakdown,
        dict,
    ):
        return {}

    item = breakdown.get(
        key,
        {},
    )

    if not isinstance(
        item,
        dict,
    ):
        return {}

    return item


# ==========================================================
# VALIDAÇÃO DOS DADOS
# ==========================================================

def validate_analysis_input(
    data,
):
    """
    Valida os dados necessários para executar
    a análise InvestIA.

    Retorna um dicionário padronizado.
    """

    if not isinstance(
        data,
        dict,
    ):

        return {

            "valid": False,

            "status":
                "INCONSISTENTE",

            "status_icon":
                "🔴",

            "message":
                "Os dados da análise não estão "
                "em formato válido.",

            "missing": [],

            "invalid": [],
        }

    # ======================================================
    # VALIDAÇÃO ESTRUTURAL
    # ======================================================

    indicator_validation = validate_indicators(
        data
    )

    # ======================================================
    # VALIDAÇÃO DOS VALORES
    # ======================================================

    value_validation = validate_analysis_values(
        data
    )

    errors = list(
        value_validation.get(
            "errors",
            [],
        )
    )

    # Evita duplicação de mensagens
    errors = list(
        dict.fromkeys(
            errors
        )
    )

    # ======================================================
    # DADOS AUSENTES
    # ======================================================

    missing = indicator_validation.get(
        "missing",
        [],
    )

    # ======================================================
    # DADOS INVÁLIDOS
    # ======================================================

    invalid = indicator_validation.get(
        "invalid",
        [],
    )

    # ======================================================
    # RESULTADO
    # ======================================================

    if missing:

        return {

            "valid": False,

            "status":
                "INCOMPLETO",

            "status_icon":
                "🟡",

            "message":
                "Dados obrigatórios ausentes: "
                + ", ".join(
                    missing
                ),

            "missing":
                missing,

            "invalid":
                invalid,

            "errors":
                errors,
        }

    if invalid or not value_validation.get(
        "valid",
        False,
    ):

        return {

            "valid": False,

            "status":
                "INCONSISTENTE",

            "status_icon":
                "🔴",

            "message":
                (
                    "Um ou mais indicadores "
                    "possuem valores inválidos."
                ),

            "missing":
                missing,

            "invalid":
                invalid,

            "errors":
                errors,
        }

    return {

        "valid": True,

        "status":
            "CONSISTENTE",

        "status_icon":
            "🟢",

        "message":
            "Dados válidos para análise.",

        "missing": [],

        "invalid": [],

        "errors": [],
    }


# ==========================================================
# TENDÊNCIA
# ==========================================================

def determine_trend(
    data,
):
    """
    Determina a tendência com base na relação
    entre preço, MA21 e MA200.

    Regras:

        Preço > MA21 e MA200
            -> Alta

        Preço < MA21 e MA200
            -> Baixa

        Demais situações
            -> Neutra
    """

    if not isinstance(
        data,
        dict,
    ):
        return "Neutra"

    price = safe_float(
        data.get("price")
    )

    ma21 = safe_float(
        data.get("ma21")
    )

    ma200 = safe_float(
        data.get("ma200")
    )

    if (
        price is None
        or ma21 is None
        or ma200 is None
    ):

        return "Indisponível"

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

    return "Neutra"


# ==========================================================
# STATUS DO RSI
# ==========================================================

def determine_rsi_status(
    rsi,
):
    """
    Classifica o RSI.
    """

    if not is_valid_number(
        rsi
    ):

        return "Indisponível"

    rsi = float(
        rsi
    )

    if rsi <= 30:

        return "Sobrevenda"

    if rsi >= 70:

        return "Sobrecompra"

    if rsi >= 50:

        return "Positivo"

    return "Negativo"


# ==========================================================
# RISCO
# ==========================================================

def determine_risk(
    data,
    score,
    trend,
):
    """
    Determina o nível de risco.

    Nesta fase o risco considera:

        - Score
        - Tendência
        - Volatilidade, quando disponível
    """

    if not is_valid_number(
        score
    ):

        return "Indisponível"

    score = float(
        score
    )

    volatility = safe_float(
        data.get("volatility")
        if isinstance(
            data,
            dict,
        )
        else None
    )

    # ======================================================
    # VOLATILIDADE ALTA
    # ======================================================

    if volatility is not None:

        # A volatilidade normalmente chega
        # em formato decimal.
        #
        # Exemplo:
        # 0.02 = 2%

        if volatility >= 0.05:

            return "Alto"

        if volatility >= 0.03:

            if score < 50:

                return "Alto"

            return "Moderado"

    # ======================================================
    # SCORE
    # ======================================================

    if score < 35:

        return "Alto"

    if score < 50:

        return "Moderado"

    # ======================================================
    # TENDÊNCIA
    # ======================================================

    if trend == "Baixa":

        if score < 65:

            return "Moderado"

    if trend == "Alta":

        if score >= 65:

            return "Baixo"

    return "Moderado"


# ==========================================================
# RECOMENDAÇÃO
# ==========================================================

def determine_recommendation(
    score,
    signal,
    risk,
):
    """
    Define a recomendação final.

    A recomendação considera Score + sinal + risco.
    """

    if not is_valid_number(
        score
    ):

        return "Aguardar"

    score = float(
        score
    )

    signal = _safe_text(
        signal,
        "INDISPONÍVEL",
    ).upper()

    risk = _safe_text(
        risk,
        "INDISPONÍVEL",
    ).upper()

    # ======================================================
    # DADOS INDISPONÍVEIS
    # ======================================================

    if (
        "INDISPONÍVEL" in signal
        or "INDISPONIVEL" in signal
        or "INDISPONÍVEL" in risk
        or "INDISPONIVEL" in risk
    ):

        return "Aguardar"

    # ======================================================
    # SINAL NEGATIVO
    # ======================================================

    if (
        "NEGATIVO" in signal
        or "VENDA" in signal
    ):

        if score <= 35:

            return "Evitar"

        return "Aguardar"

    # ======================================================
    # SINAL POSITIVO
    # ======================================================

    if (
        "POSITIVO" in signal
        or "COMPRA" in signal
    ):

        if (
            score >= 80
            and "ALTO" not in risk
        ):

            return "Compra forte"

        if (
            score >= 65
            and "ALTO" not in risk
        ):

            return "Compra"

        return "Aguardar"

    # ======================================================
    # NEUTRO
    # ======================================================

    return "Aguardar"


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

    # ======================================================
    # MA21
    # ======================================================

    ma21 = _get_breakdown_item(
        breakdown,
        "ma21",
    )

    ma21_reason = ma21.get(
        "reason"
    )

    if ma21_reason:

        reasons.append(
            _safe_text(
                ma21_reason
            )
        )

    # ======================================================
    # MA200
    # ======================================================

    ma200 = _get_breakdown_item(
        breakdown,
        "ma200",
    )

    ma200_reason = ma200.get(
        "reason"
    )

    if ma200_reason:

        reasons.append(
            _safe_text(
                ma200_reason
            )
        )

    # ======================================================
    # RSI
    # ======================================================

    rsi = _get_breakdown_item(
        breakdown,
        "rsi",
    )

    rsi_reason = rsi.get(
        "reason"
    )

    if rsi_reason:

        reasons.append(
            _safe_text(
                rsi_reason
            )
        )

    # ======================================================
    # TENDÊNCIA
    # ======================================================

    if trend != "Indisponível":

        reasons.append(
            f"Tendência identificada: {trend}."
        )

    # ======================================================
    # RSI STATUS
    # ======================================================

    if rsi_status != "Indisponível":

        reasons.append(
            f"Status do RSI: {rsi_status}."
        )

    # ======================================================
    # FALLBACK
    # ======================================================

    if not reasons:

        reasons.append(
            "Não existem informações "
            "suficientes para fundamentar a análise."
        )

    # ======================================================
    # REMOÇÃO DE DUPLICIDADES
    # ======================================================

    return list(
        dict.fromkeys(
            reasons
        )
    )


# ==========================================================
# RESUMO EXECUTIVO
# ==========================================================

def build_executive_summary(
    asset,
    price,
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

    asset = _safe_text(
        asset,
        "Ativo",
    )

    if not is_valid_number(
        price
    ):

        return (
            f"{asset}: não foi possível gerar "
            "um resumo confiável porque o preço "
            "não está disponível."
        )

    if not is_valid_number(
        score
    ):

        return (
            f"{asset}: dados insuficientes "
            "para calcular o Score InvestIA "
            "e gerar uma recomendação confiável."
        )

    price = float(
        price
    )

    score = int(
        round(
            float(score)
        )
    )

    return (
        f"{asset} apresenta preço de "
        f"R$ {price:,.2f}. "
        f"O Score InvestIA é {score}/100, "
        f"classificado como {classification}. "
        f"A tendência atual é {trend}, "
        f"com sinal {signal}. "
        f"O nível de risco é {risk} "
        f"e a recomendação é {recommendation}."
    ).replace(
        ",",
        "X",
    ).replace(
        ".",
        ",",
    ).replace(
        "X",
        ".",
    )


# ==========================================================
# ANÁLISE INDISPONÍVEL
# ==========================================================

def build_unavailable_analysis(
    asset,
    validation,
):
    """
    Retorna uma estrutura completa quando a análise
    não pode ser realizada.
    """

    asset = _safe_text(
        asset,
        "Ativo",
    )

    status = validation.get(
        "status",
        "INCONSISTENTE",
    )

    status_icon = validation.get(
        "status_icon",
        "🔴",
    )

    message = validation.get(
        "message",
        "Dados insuficientes para análise.",
    )

    missing = validation.get(
        "missing",
        [],
    )

    invalid = validation.get(
        "invalid",
        [],
    )

    reasons = []

    if missing:

        reasons.append(
            "Dados ausentes: "
            + ", ".join(
                missing
            )
            + "."
        )

    if invalid:

        reasons.append(
            "Dados inválidos: "
            + ", ".join(
                invalid
            )
            + "."
        )

    if not reasons:

        reasons.append(
            message
        )

    return {

        "asset":
            asset,

        "valid":
            False,

        "status":
            status,

        "status_icon":
            status_icon,

        "message":
            message,

        "score":
            None,

        "classification":
            "INDISPONÍVEL",

        "signal":
            "INDISPONÍVEL",

        "qualified_signal":
            "INDISPONÍVEL",

        "signal_level":
            "Indisponível",

        "signal_icon":
            "⚪",

        "trend":
            "Indisponível",

        "tendencia":
            "Indisponível",

        "recommendation":
            "Aguardar",

        "recomendacao":
            "Aguardar",

        "risk":
            "Indisponível",

        "risco":
            "Indisponível",

        "rsi_status":
            "Indisponível",

        "reasons":
            reasons,

        "justificativas":
            reasons,

        "breakdown":
            {
                "base": 50,
                "raw_score": None,
                "score": None,
            },

        "executive_summary":
            (
                f"{asset}: análise indisponível. "
                f"{message}"
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

        1. Validação
        2. Score
        3. Tendência
        4. RSI
        5. Risco
        6. Recomendação
        7. Justificativas
        8. Resumo executivo

    IMPORTANTE:

        Dados inválidos não geram Score artificial.
    """

    # ======================================================
    # VALIDAÇÃO
    # ======================================================

    validation = validate_analysis_input(
        data
    )

    if not validation["valid"]:

        return build_unavailable_analysis(
            asset,
            validation,
        )

    # ======================================================
    # NORMALIZAÇÃO
    # ======================================================

    clean_data = dict(
        data
    )

    price = safe_float(
        clean_data.get("price")
    )

    rsi = safe_float(
        clean_data.get("rsi")
    )

    ma21 = safe_float(
        clean_data.get("ma21")
    )

    ma200 = safe_float(
        clean_data.get("ma200")
    )

    volatility = safe_float(
        clean_data.get("volatility")
    )

    clean_data["price"] = price
    clean_data["rsi"] = rsi
    clean_data["ma21"] = ma21
    clean_data["ma200"] = ma200
    clean_data["volatility"] = volatility

    # ======================================================
    # SCORE
    # ======================================================

    score_details = calculate_score_details(
        clean_data
    )

    score = score_details.get(
        "score"
    )

    breakdown = score_details.get(
        "breakdown",
        {},
    )

    # ======================================================
    # PROTEÇÃO
    # ======================================================

    if not score_details.get(
        "valid",
        False,
    ) or not is_valid_number(
        score
    ):

        return build_unavailable_analysis(
            asset,
            {
                "valid": False,
                "status":
                    score_details.get(
                        "status",
                        "INCONSISTENTE",
                    ),
                "status_icon":
                    score_details.get(
                        "status_icon",
                        "🔴",
                    ),
                "message":
                    score_details.get(
                        "message",
                        "Não foi possível calcular o Score.",
                    ),
                "missing":
                    score_details.get(
                        "missing",
                        [],
                    ),
                "invalid":
                    score_details.get(
                        "invalid",
                        [],
                    ),
            },
        )

    # ======================================================
    # CLASSIFICAÇÃO
    # ======================================================

    classification = score_details.get(
        "classification",
        "INDISPONÍVEL",
    )

    # ======================================================
    # SINAL
    # ======================================================

    signal = score_details.get(
        "signal",
        "INDISPONÍVEL",
    )

    qualified_signal = signal

    signal_level = score_details.get(
        "signal_level",
        "Indisponível",
    )

    signal_icon = score_details.get(
        "signal_icon",
        "⚪",
    )

    # ======================================================
    # TENDÊNCIA
    # ======================================================

    trend = determine_trend(
        clean_data
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
        clean_data,
        score,
        trend,
    )

    # ======================================================
    # RECOMENDAÇÃO
    # ======================================================

    recommendation = determine_recommendation(
        score,
        signal,
        risk,
    )

    # ======================================================
    # JUSTIFICATIVAS
    # ======================================================

    reasons = build_reasons(
        clean_data,
        breakdown,
        trend,
        rsi_status,
    )

    # ======================================================
    # RESUMO EXECUTIVO
    # ======================================================

    executive_summary = build_executive_summary(
        asset,
        price,
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

        "valid":
            True,

        "status":
            "CONSISTENTE",

        "status_icon":
            "🟢",

        "message":
            "Análise concluída com dados válidos.",

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

        "reasons":
            reasons,

        "justificativas":
            reasons,

        "breakdown":
            breakdown,

        "executive_summary":
            executive_summary,
    }
