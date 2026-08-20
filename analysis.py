"""
InvestIA PRO
Motor de Análise

Versão: v0.6
Fase: 2.9.7 - Motor de Análise Robusto
"""

from score import (
    calculate_score_details,
)


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def safe_float(value):
    """
    Converte um valor para float com segurança.
    """

    try:

        if value is None:
            return None

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return None


def get_data_value(
    data,
    key,
    default=None,
):
    """
    Obtém um valor de um dicionário
    de maneira segura.
    """

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
# VALIDAÇÃO
# ==========================================================

def validate_analysis_input(
    data,
):
    """
    Valida os dados necessários para
    executar a análise.
    """

    if data is None:

        return False

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

        value = data.get(
            field
        )

        if value is None:

            return False

        try:

            float(value)

        except (
            TypeError,
            ValueError,
        ):

            return False

    return True


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

    if rsi <= 30:

        return "Sobrevendido"

    if rsi >= 70:

        return "Sobrecomprado"

    if rsi >= 60:

        return "Pressão compradora"

    if rsi <= 40:

        return "Pressão vendedora"

    return "Neutro"


# ==========================================================
# TENDÊNCIA
# ==========================================================

def determine_trend(
    price,
    ma21,
    ma200,
):
    """
    Determina a tendência combinando
    preço, MA21 e MA200.
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

        return "Indisponível"

    # ======================================================
    # ALTA
    # ======================================================

    if (
        price > ma21
        and price > ma200
    ):

        if ma21 > ma200:

            return "Alta forte"

        return "Alta"

    # ======================================================
    # BAIXA
    # ======================================================

    if (
        price < ma21
        and price < ma200
    ):

        if ma21 < ma200:

            return "Baixa forte"

        return "Baixa"

    # ======================================================
    # TRANSIÇÃO
    # ======================================================

    if (
        price > ma21
        and price < ma200
    ):

        return "Recuperação"

    if (
        price < ma21
        and price > ma200
    ):

        return "Correção"

    return "Neutra"


# ==========================================================
# RISCO
# ==========================================================

def determine_risk(
    volatility,
    rsi,
    trend,
):
    """
    Define o nível de risco do ativo.

    A avaliação combina:

    - Volatilidade
    - RSI
    - Tendência
    """

    volatility = safe_float(
        volatility
    )

    rsi = safe_float(
        rsi
    )

    if volatility is None:

        return "Moderado"

    risk_points = 0

    # ======================================================
    # VOLATILIDADE
    # ======================================================

    if volatility >= 0.04:

        risk_points += 3

    elif volatility >= 0.025:

        risk_points += 2

    elif volatility >= 0.015:

        risk_points += 1

    # ======================================================
    # RSI
    # ======================================================

    if rsi is not None:

        if rsi >= 75:

            risk_points += 2

        elif rsi <= 25:

            risk_points += 2

        elif (
            rsi >= 70
            or rsi <= 30
        ):

            risk_points += 1

    # ======================================================
    # TENDÊNCIA
    # ======================================================

    if trend in [
        "Baixa forte",
        "Correção",
    ]:

        risk_points += 2

    elif trend == "Baixa":

        risk_points += 1

    # ======================================================
    # CLASSIFICAÇÃO
    # ======================================================

    if risk_points >= 5:

        return "Alto"

    if risk_points >= 3:

        return "Moderado"

    return "Baixo"


# ==========================================================
# RECOMENDAÇÃO
# ==========================================================

def determine_recommendation(
    score,
    signal,
    risk,
    trend,
):
    """
    Define a recomendação principal
    do InvestIA PRO.
    """

    score = safe_float(
        score
    )

    if score is None:

        return "Aguardar"

    # ======================================================
    # COMPRA
    # ======================================================

    if (
        signal == "POSITIVO"
        and risk == "Baixo"
        and score >= 70
    ):

        return "Cenário favorável"

    if (
        signal == "POSITIVO"
        and score >= 60
    ):

        return "Avaliar oportunidade"

    # ======================================================
    # VENDA / ALERTA
    # ======================================================

    if (
        signal == "NEGATIVO"
        and risk == "Alto"
    ):

        return "Evitar exposição"

    if (
        signal == "NEGATIVO"
        and trend in [
            "Baixa",
            "Baixa forte",
        ]
    ):

        return "Atenção ao risco"

    # ======================================================
    # NEUTRO
    # ======================================================

    if risk == "Alto":

        return "Aguardar confirmação"

    return "Acompanhar"


# ==========================================================
# JUSTIFICATIVAS
# ==========================================================

def build_reasons(
    price,
    ma21,
    ma200,
    rsi,
    volatility,
    trend,
    risk,
    breakdown,
):
    """
    Monta as justificativas da análise.
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

    volatility = safe_float(
        volatility
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
                "Preço acima da média móvel de 21 períodos, indicando força no curto prazo."
            )

        elif price < ma21:

            reasons.append(
                "Preço abaixo da média móvel de 21 períodos, indicando pressão no curto prazo."
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
                "Preço acima da média móvel de 200 períodos, favorecendo a estrutura de longo prazo."
            )

        elif price < ma200:

            reasons.append(
                "Preço abaixo da média móvel de 200 períodos, sinalizando fragilidade na estrutura de longo prazo."
            )

    # ======================================================
    # RSI
    # ======================================================

    rsi_status = get_rsi_status(
        rsi
    )

    if rsi_status == "Sobrevendido":

        reasons.append(
            "RSI em região de sobrevenda, podendo indicar possibilidade de recuperação técnica."
        )

    elif rsi_status == "Sobrecomprado":

        reasons.append(
            "RSI em região de sobrecompra, aumentando o risco de realização de lucros."
        )

    elif rsi_status == "Pressão compradora":

        reasons.append(
            "RSI demonstra predominância de pressão compradora."
        )

    elif rsi_status == "Pressão vendedora":

        reasons.append(
            "RSI demonstra predominância de pressão vendedora."
        )

    else:

        reasons.append(
            "RSI permanece em região neutra, sem extremo técnico relevante."
        )

    # ======================================================
    # TENDÊNCIA
    # ======================================================

    if trend == "Alta forte":

        reasons.append(
            "A estrutura técnica indica tendência de alta com alinhamento entre curto e longo prazo."
        )

    elif trend == "Alta":

        reasons.append(
            "O ativo apresenta estrutura técnica predominantemente positiva."
        )

    elif trend == "Baixa forte":

        reasons.append(
            "A estrutura técnica indica tendência de baixa consolidada."
        )

    elif trend == "Baixa":

        reasons.append(
            "O ativo apresenta predominância de sinais técnicos negativos."
        )

    elif trend == "Recuperação":

        reasons.append(
            "O ativo mostra recuperação no curto prazo, mas ainda enfrenta resistência na tendência de longo prazo."
        )

    elif trend == "Correção":

        reasons.append(
            "O ativo passa por correção no curto prazo dentro de uma estrutura técnica ainda indefinida."
        )

    else:

        reasons.append(
            "Os indicadores apresentam sinais mistos, caracterizando tendência neutra."
        )

    # ======================================================
    # VOLATILIDADE
    # ======================================================

    if volatility is not None:

        volatility_percent = (
            volatility * 100
        )

        if volatility_percent >= 4:

            reasons.append(
                f"Volatilidade elevada ({volatility_percent:.2f}% ao dia), aumentando o risco operacional."
            )

        elif volatility_percent >= 2.5:

            reasons.append(
                f"Volatilidade moderada/alta ({volatility_percent:.2f}% ao dia)."
            )

        else:

            reasons.append(
                f"Volatilidade controlada ({volatility_percent:.2f}% ao dia)."
            )

    # ======================================================
    # RISCO
    # ======================================================

    reasons.append(
        f"Classificação geral de risco: {risk}."
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

    asset_name = (
        str(asset).upper().strip()
        if asset
        else "ATIVO"
    )

    score = safe_float(
        score
    )

    if score is None:

        score = 0

    return (
        f"O ativo {asset_name} apresenta "
        f"Score InvestIA de {int(round(score))}/100, "
        f"classificado como {classification}. "
        f"O cenário técnico atual indica "
        f"tendência de {trend.lower()}, "
        f"com sinal {signal.lower()} e "
        f"nível de risco {risk.lower()}. "
        f"A recomendação atual é: {recommendation}."
    )


# ==========================================================
# MOTOR PRINCIPAL
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
        "ma21": float,
        "ma200": float,
        "rsi": float,
        "volatility": float
    }

    Retorna Score, classificação, sinal,
    tendência, risco, recomendação,
    justificativas e resumo executivo.
    """

    # ======================================================
    # VALIDAÇÃO
    # ======================================================

    if not validate_analysis_input(
        data
    ):

        raise ValueError(
            "Dados insuficientes para executar a análise do ativo."
        )

    # ======================================================
    # DADOS
    # ======================================================

    price = safe_float(
        get_data_value(
            data,
            "price"
        )
    )

    ma21 = safe_float(
        get_data_value(
            data,
            "ma21"
        )
    )

    ma200 = safe_float(
        get_data_value(
            data,
            "ma200"
        )
    )

    rsi = safe_float(
        get_data_value(
            data,
            "rsi"
        )
    )

    volatility = safe_float(
        get_data_value(
            data,
            "volatility"
        )
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

    signal_level = score_details.get(
        "signal_level",
        "Aguardar",
    )

    signal_icon = score_details.get(
        "signal_icon",
        "🟡",
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

    rsi_status = get_rsi_status(
        rsi
    )

    # ======================================================
    # RISCO
    # ======================================================

    risk = determine_risk(
        volatility,
        rsi,
        trend,
    )

    # ======================================================
    # RECOMENDAÇÃO
    # ======================================================

    recommendation = determine_recommendation(
        score,
        signal,
        risk,
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
        volatility,
        trend,
        risk,
        breakdown,
    )

    # ======================================================
    # RESUMO EXECUTIVO
    # ======================================================

    executive_summary = build_executive_summary(
        asset,
        score,
        classification,
        signal,
        trend,
        risk,
        recommendation,
    )

    # ======================================================
    # RETORNO FINAL
    # ======================================================

    return {

        # Identificação
        "asset":
            asset,

        # Score
        "score":
            score,

        "classification":
            classification,

        "signal":
            signal,

        "qualified_signal":
            signal,

        "signal_level":
            signal_level,

        "signal_icon":
            signal_icon,

        "breakdown":
            breakdown,

        # Análise técnica
        "trend":
            trend,

        "tendencia":
            trend,

        "rsi_status":
            rsi_status,

        # Risco
        "risk":
            risk,

        "risco":
            risk,

        # Recomendação
        "recommendation":
            recommendation,

        "recomendacao":
            recommendation,

        # Explicação
        "reasons":
            reasons,

        "justificativas":
            reasons,

        # Resumo
        "executive_summary":
            executive_summary,
    }
