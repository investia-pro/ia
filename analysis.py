"""
InvestIA PRO
Motor de Análise

Versão: v0.6
Fase: 2.9.5 - Integração da Validação dos Indicadores
"""

from score import (
    calculate_score_details,
    validate_score_data,
    classify_score,
    classify_signal,
)

from config import (
    RSI_OVERSOLD,
    RSI_OVERBOUGHT,
)


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def _safe_float(
    value,
    default=None,
):
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


def _safe_text(
    value,
    default="",
):
    """
    Converte um valor para texto.
    """

    if value is None:
        return default

    return str(
        value
    ).strip()


def _get_value(
    data,
    *keys,
    default=None,
):
    """
    Obtém um valor de um dicionário
    utilizando múltiplas possibilidades
    de nome.
    """

    if not isinstance(
        data,
        dict,
    ):

        return default

    for key in keys:

        if key in data:

            return data[key]

    return default


# ==========================================================
# VALIDAÇÃO DA ANÁLISE
# ==========================================================

def validate_analysis_input(
    data,
):
    """
    Valida os dados necessários para
    executar a análise InvestIA.
    """

    validation = validate_score_data(
        data
    )

    return validation


# ==========================================================
# TENDÊNCIA
# ==========================================================

def determine_trend(
    price,
    ma21,
    ma200,
):
    """
    Determina a tendência com base
    no preço e nas médias móveis.
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

        return "Indeterminada"

    # ======================================================
    # ALTA FORTE
    # ======================================================

    if (
        price > ma21
        and price > ma200
        and ma21 > ma200
    ):

        return "Alta forte"

    # ======================================================
    # ALTA
    # ======================================================

    if (
        price > ma21
        and price > ma200
    ):

        return "Alta"

    # ======================================================
    # BAIXA FORTE
    # ======================================================

    if (
        price < ma21
        and price < ma200
        and ma21 < ma200
    ):

        return "Baixa forte"

    # ======================================================
    # BAIXA
    # ======================================================

    if (
        price < ma21
        and price < ma200
    ):

        return "Baixa"

    # ======================================================
    # TRANSIÇÃO
    # ======================================================

    return "Lateral / Transição"


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

    if rsi <= RSI_OVERSOLD:

        return "Sobrevenda"

    if rsi >= RSI_OVERBOUGHT:

        return "Sobrecompra"

    if rsi >= 50:

        return "Neutro positivo"

    return "Neutro negativo"


# ==========================================================
# RISCO
# ==========================================================

def determine_risk(
    score,
    volatility,
    trend,
):
    """
    Determina o nível de risco.

    O risco considera:
        - Score
        - Volatilidade
        - Tendência
    """

    score = _safe_float(
        score
    )

    volatility = _safe_float(
        volatility
    )

    trend = _safe_text(
        trend
    )

    if score is None:

        return "Indeterminado"

    # ------------------------------------------------------
    # VOLATILIDADE
    # ------------------------------------------------------

    if volatility is not None:

        if volatility >= 0.05:

            return "Alto"

        if volatility >= 0.03:

            return "Moderado/Alto"

    # ------------------------------------------------------
    # TENDÊNCIA
    # ------------------------------------------------------

    if (
        "Baixa forte"
        in trend
    ):

        return "Alto"

    # ------------------------------------------------------
    # SCORE
    # ------------------------------------------------------

    if score <= 35:

        return "Alto"

    if score <= 50:

        return "Moderado"

    if score >= 80:

        return "Baixo"

    return "Moderado"


# ==========================================================
# RECOMENDAÇÃO
# ==========================================================

def determine_recommendation(
    score,
    signal,
    trend,
    risk,
):
    """
    Define a recomendação final.
    """

    score = _safe_float(
        score
    )

    signal = _safe_text(
        signal
    ).upper()

    trend = _safe_text(
        trend
    )

    risk = _safe_text(
        risk
    )

    if score is None:

        return "Aguardar"

    # ======================================================
    # RISCO ALTO
    # ======================================================

    if risk == "Alto":

        if score >= 80:

            return "Compra com cautela"

        if score <= 35:

            return "Evitar"

        return "Aguardar"

    # ======================================================
    # SCORE FORTE
    # ======================================================

    if score >= 80:

        return "Compra"

    # ======================================================
    # SCORE BOM
    # ======================================================

    if score >= 65:

        if (
            "Alta"
            in trend
        ):

            return "Compra"

        return "Compra moderada"

    # ======================================================
    # SCORE FRACO
    # ======================================================

    if score <= 35:

        return "Venda / Evitar"

    # ======================================================
    # SCORE MUITO FRACO
    # ======================================================

    if score < 50:

        if signal == "NEGATIVO":

            return "Evitar"

        return "Aguardar"

    # ======================================================
    # NEUTRO
    # ======================================================

    return "Aguardar"


# ==========================================================
# SINAL QUALIFICADO
# ==========================================================

def determine_qualified_signal(
    score,
    signal,
    trend,
):
    """
    Qualifica o sinal considerando
    o Score e a tendência.
    """

    score = _safe_float(
        score
    )

    signal = _safe_text(
        signal,
        "NEUTRO",
    ).upper()

    trend = _safe_text(
        trend
    )

    if score is None:

        return "INDEFINIDO"

    if signal == "POSITIVO":

        if (
            "Alta"
            in trend
        ):

            return "COMPRA FORTE"

        return "POSITIVO"

    if signal == "NEGATIVO":

        if (
            "Baixa"
            in trend
        ):

            return "VENDA FORTE"

        return "NEGATIVO"

    return "NEUTRO"


# ==========================================================
# NÍVEL DO SINAL
# ==========================================================

def determine_signal_level(
    score,
):
    """
    Determina o nível de intensidade
    do Score.
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

def determine_signal_icon(
    signal,
):
    """
    Retorna um ícone conforme o sinal.
    """

    signal = _safe_text(
        signal
    ).upper()

    if (
        "POSITIVO"
        in signal
        or "COMPRA"
        in signal
    ):

        return "🟢"

    if (
        "NEGATIVO"
        in signal
        or "VENDA"
        in signal
    ):

        return "🔴"

    if signal == "INDEFINIDO":

        return "⚪"

    return "🟡"


# ==========================================================
# JUSTIFICATIVAS
# ==========================================================

def generate_reasons(
    data,
    trend,
    rsi_status,
    score_details,
):
    """
    Gera as justificativas da análise.
    """

    reasons = []

    price = _safe_float(
        _get_value(
            data,
            "price",
        )
    )

    ma21 = _safe_float(
        _get_value(
            data,
            "ma21",
        )
    )

    ma200 = _safe_float(
        _get_value(
            data,
            "ma200",
        )
    )

    rsi = _safe_float(
        _get_value(
            data,
            "rsi",
        )
    )

    # ======================================================
    # PREÇO x MA21
    # ======================================================

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
                "indicando pressão de curto prazo."
            )

        else:

            reasons.append(
                "O preço está alinhado à MA21."
            )

    # ======================================================
    # PREÇO x MA200
    # ======================================================

    if (
        price is not None
        and ma200 is not None
    ):

        if price > ma200:

            reasons.append(
                "O preço está acima da MA200, "
                "mantendo viés positivo de longo prazo."
            )

        elif price < ma200:

            reasons.append(
                "O preço está abaixo da MA200, "
                "indicando viés negativo de longo prazo."
            )

        else:

            reasons.append(
                "O preço está alinhado à MA200."
            )

    # ======================================================
    # RSI
    # ======================================================

    if rsi is not None:

        if rsi <= RSI_OVERSOLD:

            reasons.append(
                f"RSI em {rsi:.2f}, "
                "indicando região de sobrevenda."
            )

        elif rsi >= RSI_OVERBOUGHT:

            reasons.append(
                f"RSI em {rsi:.2f}, "
                "indicando região de sobrecompra."
            )

        else:

            reasons.append(
                f"RSI em {rsi:.2f}, "
                "em região sem extremo de momentum."
            )

    # ======================================================
    # TENDÊNCIA
    # ======================================================

    if trend:

        reasons.append(
            f"Tendência identificada: {trend}."
        )

    # ======================================================
    # SCORE
    # ======================================================

    if isinstance(
        score_details,
        dict,
    ):

        score = score_details.get(
            "score"
        )

        if score is not None:

            reasons.append(
                f"Score InvestIA calculado em "
                f"{score}/100."
            )

    return reasons


# ==========================================================
# RESUMO EXECUTIVO
# ==========================================================

def generate_executive_summary(
    asset,
    price,
    score,
    classification,
    trend,
    recommendation,
    risk,
    rsi_status,
):
    """
    Gera o resumo executivo.
    """

    asset = _safe_text(
        asset,
        "Ativo",
    )

    price = _safe_float(
        price
    )

    score = _safe_float(
        score
    )

    classification = _safe_text(
        classification,
        "Indisponível",
    )

    trend = _safe_text(
        trend,
        "Indeterminada",
    )

    recommendation = _safe_text(
        recommendation,
        "Aguardar",
    )

    risk = _safe_text(
        risk,
        "Indeterminado",
    )

    rsi_status = _safe_text(
        rsi_status,
        "Indisponível",
    )

    if price is None:

        price_text = "indisponível"

    else:

        price_text = (
            f"R$ {price:,.2f}"
            .replace(
                ",",
                "X",
            )
            .replace(
                ".",
                ",",
            )
            .replace(
                "X",
                ".",
            )
        )

    if score is None:

        return (
            f"{asset}: os dados disponíveis "
            "não são suficientes para gerar "
            "uma análise confiável. "
            "Recomendação: aguardar."
        )

    return (
        f"{asset} apresenta preço de "
        f"{price_text}, Score InvestIA de "
        f"{int(round(score))}/100 e classificação "
        f"{classification}. "
        f"A tendência atual é {trend}, "
        f"com RSI em condição de {rsi_status}. "
        f"O nível de risco é {risk}. "
        f"A recomendação atual é "
        f"{recommendation}."
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

    Mantém compatibilidade com:

        analyze_asset(data)

    e:

        analyze_asset(data, asset)
    """

    # ======================================================
    # VALIDAÇÃO
    # ======================================================

    validation = validate_analysis_input(
        data
    )

    # ======================================================
    # DADOS INVÁLIDOS
    # ======================================================

    if not validation["valid"]:

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

        return {

            "asset":
                asset or "",

            "score":
                None,

            "classification":
                "INDISPONÍVEL",

            "signal":
                "INDEFINIDO",

            "qualified_signal":
                "INDEFINIDO",

            "signal_level":
                "Indisponível",

            "signal_icon":
                status_icon,

            "trend":
                "Indeterminada",

            "recommendation":
                "Aguardar",

            "risk":
                "Indeterminado",

            "rsi_status":
                "Indisponível",

            "reasons":
                [
                    message
                ],

            "breakdown":
                {},

            "executive_summary":
                (
                    f"{asset or 'Ativo'}: "
                    f"análise não realizada. "
                    f"{message}"
                ),

            "valid":
                False,

            "analysis_valid":
                False,

            "data_status":
                status,

            "data_status_icon":
                status_icon,

            "validation":
                validation,

            "message":
                message,

        }

    # ======================================================
    # SCORE
    # ======================================================

    score_details = calculate_score_details(
        data
    )

    if not score_details.get(
        "valid",
        False,
    ):

        validation = score_details.get(
            "validation",
            validation,
        )

        message = score_details.get(
            "message",
            "Não foi possível calcular o Score.",
        )

        return {

            "asset":
                asset or "",

            "score":
                None,

            "classification":
                "INDISPONÍVEL",

            "signal":
                "INDEFINIDO",

            "qualified_signal":
                "INDEFINIDO",

            "signal_level":
                "Indisponível",

            "signal_icon":
                "🔴",

            "trend":
                "Indeterminada",

            "recommendation":
                "Aguardar",

            "risk":
                "Indeterminado",

            "rsi_status":
                "Indisponível",

            "reasons":
                [
                    message
                ],

            "breakdown":
                {},

            "executive_summary":
                (
                    f"{asset or 'Ativo'}: "
                    "não foi possível calcular "
                    "um Score confiável."
                ),

            "valid":
                False,

            "analysis_valid":
                False,

            "data_status":
                validation.get(
                    "status",
                    "INCONSISTENTE",
                ),

            "data_status_icon":
                validation.get(
                    "status_icon",
                    "🔴",
                ),

            "validation":
                validation,

            "message":
                message,

        }

    # ======================================================
    # EXTRAÇÃO DOS DADOS
    # ======================================================

    price = _safe_float(
        _get_value(
            data,
            "price",
        )
    )

    ma21 = _safe_float(
        _get_value(
            data,
            "ma21",
        )
    )

    ma200 = _safe_float(
        _get_value(
            data,
            "ma200",
        )
    )

    rsi = _safe_float(
        _get_value(
            data,
            "rsi",
        )
    )

    volatility = _safe_float(
        _get_value(
            data,
            "volatility",
        )
    )

    score = score_details.get(
        "score"
    )

    # ======================================================
    # CLASSIFICAÇÃO
    # ======================================================

    classification = classify_score(
        score
    )

    signal = classify_signal(
        score
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
        score,
        volatility,
        trend,
    )

    # ======================================================
    # RECOMENDAÇÃO
    # ======================================================

    recommendation = determine_recommendation(
        score,
        signal,
        trend,
        risk,
    )

    # ======================================================
    # SINAL QUALIFICADO
    # ======================================================

    qualified_signal = determine_qualified_signal(
        score,
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

    signal_icon = determine_signal_icon(
        qualified_signal
    )

    # ======================================================
    # JUSTIFICATIVAS
    # ======================================================

    reasons = generate_reasons(
        data,
        trend,
        rsi_status,
        score_details,
    )

    # ======================================================
    # RESUMO EXECUTIVO
    # ======================================================

    executive_summary = generate_executive_summary(
        asset,
        price,
        score,
        classification,
        trend,
        recommendation,
        risk,
        rsi_status,
    )

    # ======================================================
    # RETORNO FINAL
    # ======================================================

    return {

        "asset":
            asset or "",

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
            score_details.get(
                "breakdown",
                {},
            ),

        "executive_summary":
            executive_summary,

        "valid":
            True,

        "analysis_valid":
            True,

        "data_status":
            "CONSISTENTE",

        "data_status_icon":
            "🟢",

        "validation":
            score_details.get(
                "validation",
                validation,
            ),

        "message":
            "Análise concluída com dados consistentes.",

    }


# ==========================================================
# ALIAS DE COMPATIBILIDADE
# ==========================================================

def analyze(
    data,
    asset=None,
):
    """
    Alias para manter compatibilidade
    com chamadas antigas.
    """

    return analyze_asset(
        data,
        asset,
    )
