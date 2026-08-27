"""
InvestIA PRO
Motor de Análise

Versão: v3.1.3
Fase Final: 3.1.3

Responsabilidades:
- Consolidar indicadores técnicos
- Consolidar dados fundamentalistas
- Calcular Score Técnico
- Calcular Score Fundamentalista
- Calcular Score Integrado
- Definir tendência
- Definir nível de risco
- Gerar recomendação
- Gerar resumo executivo
- Gerar fatores principais

Compatível com:
- market.py Fase 3.0.7
- indicators.py Fase 3.0.7
- score.py Fase 3.0.7
- app.py Fase 3.0.6+
"""

import math


# ==========================================================
# IMPORTAÇÃO DO MOTOR DE SCORE
# ==========================================================

try:

    from score import (
        calculate_investia_scores,
        get_signal_icon,
    )

except Exception as error:

    raise ImportError(
        "Não foi possível importar o módulo score.py. "
        "Verifique se o arquivo score.py da Fase 3.0.7 "
        "está na mesma pasta do analysis.py."
    ) from error


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def safe_float(value, default=None):
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

    if not math.isfinite(value):
        return default

    return value


def clamp(
    value,
    minimum=0,
    maximum=100,
):
    """
    Limita um valor dentro de um intervalo.
    """

    value = safe_float(
        value,
        minimum,
    )

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


def safe_upper(value, default="N/D"):
    """
    Converte texto para maiúsculo com segurança.
    """

    if value is None:
        return default

    try:

        value = str(value).strip()

        if not value:
            return default

        return value.upper()

    except Exception:
        return default


def normalize_percent(value):
    """
    Normaliza um percentual.

    Exemplos:

    0.15 -> 15.0
    15   -> 15.0
    """

    value = safe_float(value)

    if value is None:
        return None

    if abs(value) <= 1:
        return value * 100

    return value


# ==========================================================
# EXTRAÇÃO SEGURA
# ==========================================================

def get_indicators(data):
    """
    Obtém os indicadores técnicos.

    Aceita tanto:

    {
        "indicators": {...}
    }

    quanto:

    {
        "rsi": ...,
        "ma21": ...
    }
    """

    if not isinstance(data, dict):
        return {}

    indicators = data.get(
        "indicators"
    )

    if isinstance(
        indicators,
        dict,
    ):
        return indicators

    return data


def get_fundamentals(data):
    """
    Obtém os fundamentos do ativo.
    """

    if not isinstance(data, dict):
        return {}

    fundamentals = data.get(
        "fundamentals",
        {},
    )

    if not isinstance(
        fundamentals,
        dict,
    ):
        return {}

    return fundamentals


# ==========================================================
# TENDÊNCIA
# ==========================================================

def determine_trend(indicators):
    """
    Determina a tendência consolidada.

    Utiliza preferencialmente:

    - short_trend
    - long_trend

    Caso não estejam disponíveis,
    utiliza preço, MA21 e MA200.
    """

    if not isinstance(
        indicators,
        dict,
    ):
        return "N/D"

    short_trend = safe_upper(
        indicators.get(
            "short_trend"
        )
    )

    long_trend = safe_upper(
        indicators.get(
            "long_trend"
        )
    )

    # ------------------------------------------------------
    # TENDÊNCIA FORTE DE ALTA
    # ------------------------------------------------------

    if (
        short_trend in (
            "ALTA",
            "FORTE ALTA",
        )
        and long_trend in (
            "ALTA",
            "FORTE ALTA",
        )
    ):

        if (
            short_trend == "FORTE ALTA"
            or long_trend == "FORTE ALTA"
        ):

            return "FORTE ALTA"

        return "ALTA"

    # ------------------------------------------------------
    # TENDÊNCIA FORTE DE BAIXA
    # ------------------------------------------------------

    if (
        short_trend in (
            "BAIXA",
            "FORTE BAIXA",
        )
        and long_trend in (
            "BAIXA",
            "FORTE BAIXA",
        )
    ):

        if (
            short_trend == "FORTE BAIXA"
            or long_trend == "FORTE BAIXA"
        ):

            return "FORTE BAIXA"

        return "BAIXA"

    # ------------------------------------------------------
    # DIVERGÊNCIA
    # ------------------------------------------------------

    if (
        short_trend in (
            "ALTA",
            "FORTE ALTA",
        )
        and long_trend in (
            "BAIXA",
            "FORTE BAIXA",
        )
    ):

        return "RECUPERAÇÃO"

    if (
        short_trend in (
            "BAIXA",
            "FORTE BAIXA",
        )
        and long_trend in (
            "ALTA",
            "FORTE ALTA",
        )
    ):

        return "CORREÇÃO"

    # ------------------------------------------------------
    # UM DOS DOIS INDICADORES
    # ------------------------------------------------------

    if short_trend in (
        "ALTA",
        "FORTE ALTA",
    ):

        return "ALTA"

    if short_trend in (
        "BAIXA",
        "FORTE BAIXA",
    ):

        return "BAIXA"

    if long_trend in (
        "ALTA",
        "FORTE ALTA",
    ):

        return "ALTA"

    if long_trend in (
        "BAIXA",
        "FORTE BAIXA",
    ):

        return "BAIXA"

    # ------------------------------------------------------
    # FALLBACK POR MÉDIAS
    # ------------------------------------------------------

    price = safe_float(
        indicators.get(
            "price",
            indicators.get(
                "current_price"
            ),
        )
    )

    ma21 = safe_float(
        indicators.get(
            "ma21"
        )
    )

    ma200 = safe_float(
        indicators.get(
            "ma200"
        )
    )

    if (
        price is not None
        and ma21 is not None
        and ma200 is not None
    ):

        if (
            price > ma21
            and ma21 > ma200
        ):

            return "ALTA"

        if (
            price < ma21
            and ma21 < ma200
        ):

            return "BAIXA"

        return "NEUTRA"

    return "NEUTRA"


# ==========================================================
# RISCO
# ==========================================================

def determine_risk(
    indicators,
    integrated_score=None,
):
    """
    Determina o nível de risco.

    Considera:

    - volatilidade
    - RSI
    - tendência
    - distância das médias
    - Score Integrado
    """

    if not isinstance(
        indicators,
        dict,
    ):

        return "N/D"

    risk_points = 0

    # ------------------------------------------------------
    # VOLATILIDADE
    # ------------------------------------------------------

    annual_volatility = safe_float(
        indicators.get(
            "annual_volatility"
        )
    )

    if annual_volatility is None:

        volatility = safe_float(
            indicators.get(
                "volatility"
            )
        )

        if volatility is not None:

            annual_volatility = (
                volatility
                * math.sqrt(252)
            )

    if annual_volatility is not None:

        if annual_volatility >= 0.80:

            risk_points += 4

        elif annual_volatility >= 0.50:

            risk_points += 3

        elif annual_volatility >= 0.35:

            risk_points += 2

        elif annual_volatility >= 0.20:

            risk_points += 1

    # ------------------------------------------------------
    # RSI
    # ------------------------------------------------------

    rsi = safe_float(
        indicators.get(
            "rsi"
        )
    )

    if rsi is not None:

        if rsi >= 75:

            risk_points += 2

        elif rsi <= 25:

            risk_points += 2

        elif rsi >= 70:

            risk_points += 1

        elif rsi <= 30:

            risk_points += 1

    # ------------------------------------------------------
    # TENDÊNCIA
    # ------------------------------------------------------

    trend = determine_trend(
        indicators
    )

    if trend == "FORTE BAIXA":

        risk_points += 3

    elif trend == "BAIXA":

        risk_points += 2

    elif trend == "CORREÇÃO":

        risk_points += 1

    # ------------------------------------------------------
    # SCORE INTEGRADO
    # ------------------------------------------------------

    integrated_score = safe_float(
        integrated_score
    )

    if integrated_score is not None:

        if integrated_score < 30:

            risk_points += 3

        elif integrated_score < 45:

            risk_points += 2

        elif integrated_score < 55:

            risk_points += 1

    # ------------------------------------------------------
    # CLASSIFICAÇÃO
    # ------------------------------------------------------

    if risk_points >= 7:

        return "MUITO ALTO"

    if risk_points >= 5:

        return "ALTO"

    if risk_points >= 3:

        return "MODERADO"

    return "BAIXO"


# ==========================================================
# RECOMENDAÇÃO
# ==========================================================

def determine_recommendation(
    integrated_score,
    technical_score,
    fundamental_score,
    trend,
    risk,
):
    """
    Define a recomendação executiva.

    A recomendação não depende apenas do Score.

    Considera:

    - Score Integrado
    - Score Técnico
    - Score Fundamentalista
    - Tendência
    - Risco
    """

    integrated_score = clamp(
        integrated_score
    )

    technical_score = clamp(
        technical_score
    )

    fundamental_score = clamp(
        fundamental_score
    )

    trend = safe_upper(
        trend
    )

    risk = safe_upper(
        risk
    )

    # ------------------------------------------------------
    # VENDA
    # ------------------------------------------------------

    if (
        integrated_score < 30
        and risk in (
            "ALTO",
            "MUITO ALTO",
        )
    ):

        return "REDUZIR EXPOSIÇÃO"

    if trend == "FORTE BAIXA":

        return "CAUTELA"

    # ------------------------------------------------------
    # COMPRA FORTE
    # ------------------------------------------------------

    if (
        integrated_score >= 80
        and technical_score >= 70
        and fundamental_score >= 70
        and trend in (
            "ALTA",
            "FORTE ALTA",
        )
        and risk in (
            "BAIXO",
            "MODERADO",
        )
    ):

        return "COMPRA FORTE"

    # ------------------------------------------------------
    # COMPRA
    # ------------------------------------------------------

    if (
        integrated_score >= 65
        and trend in (
            "ALTA",
            "FORTE ALTA",
            "RECUPERAÇÃO",
        )
        and risk not in (
            "ALTO",
            "MUITO ALTO",
        )
    ):

        return "COMPRA"

    # ------------------------------------------------------
    # OPORTUNIDADE FUNDAMENTALISTA
    # ------------------------------------------------------

    if (
        fundamental_score >= 70
        and technical_score < 55
        and trend in (
            "BAIXA",
            "CORREÇÃO",
        )
    ):

        return "AGUARDAR MELHOR PONTO"

    # ------------------------------------------------------
    # NEUTRO
    # ------------------------------------------------------

    if integrated_score >= 45:

        return "AGUARDAR"

    # ------------------------------------------------------
    # CAUTELA
    # ------------------------------------------------------

    if integrated_score >= 30:

        return "CAUTELA"

    return "EVITAR"


# ==========================================================
# QUALIFICAÇÃO DO SINAL
# ==========================================================

def determine_qualified_signal(
    integrated_score,
    technical_score,
    fundamental_score,
    trend,
    risk,
):
    """
    Gera uma qualificação detalhada do sinal.
    """

    integrated_score = clamp(
        integrated_score
    )

    technical_score = clamp(
        technical_score
    )

    fundamental_score = clamp(
        fundamental_score
    )

    trend = safe_upper(
        trend
    )

    risk = safe_upper(
        risk
    )

    # ------------------------------------------------------
    # SINAL MUITO FORTE
    # ------------------------------------------------------

    if (
        integrated_score >= 80
        and technical_score >= 70
        and fundamental_score >= 70
        and trend in (
            "ALTA",
            "FORTE ALTA",
        )
    ):

        return "SINAL FORTE E CONSISTENTE"

    # ------------------------------------------------------
    # SINAL POSITIVO
    # ------------------------------------------------------

    if (
        integrated_score >= 65
        and trend in (
            "ALTA",
            "FORTE ALTA",
            "RECUPERAÇÃO",
        )
    ):

        if risk in (
            "ALTO",
            "MUITO ALTO",
        ):

            return "SINAL POSITIVO COM RISCO ELEVADO"

        return "SINAL POSITIVO"

    # ------------------------------------------------------
    # FUNDAMENTOS BONS, TÉCNICO FRACO
    # ------------------------------------------------------

    if (
        fundamental_score >= 70
        and technical_score < 50
    ):

        return "FUNDAMENTOS FORTES, MAS TÉCNICO DESFAVORÁVEL"

    # ------------------------------------------------------
    # TÉCNICO BOM, FUNDAMENTOS FRACOS
    # ------------------------------------------------------

    if (
        technical_score >= 70
        and fundamental_score < 50
    ):

        return "MOMENTUM POSITIVO, MAS FUNDAMENTOS FRACOS"

    # ------------------------------------------------------
    # NEGATIVO
    # ------------------------------------------------------

    if integrated_score < 45:

        if risk in (
            "ALTO",
            "MUITO ALTO",
        ):

            return "SINAL NEGATIVO COM RISCO ELEVADO"

        return "SINAL NEGATIVO"

    return "SINAL NEUTRO"


# ==========================================================
# FATORES PRINCIPAIS
# ==========================================================

def generate_reasons(
    indicators,
    fundamentals,
    technical_score,
    fundamental_score,
    integrated_score,
    trend,
    risk,
):
    """
    Gera os principais fatores positivos e negativos
    que explicam o resultado da análise.
    """

    reasons = []

    if not isinstance(
        indicators,
        dict,
    ):

        indicators = {}

    if not isinstance(
        fundamentals,
        dict,
    ):

        fundamentals = {}

    # ------------------------------------------------------
    # TENDÊNCIA
    # ------------------------------------------------------

    trend = safe_upper(
        trend
    )

    if trend in (
        "ALTA",
        "FORTE ALTA",
    ):

        reasons.append(
            "A tendência técnica apresenta viés positivo."
        )

    elif trend == "RECUPERAÇÃO":

        reasons.append(
            "O ativo apresenta sinais de recuperação técnica."
        )

    elif trend in (
        "BAIXA",
        "FORTE BAIXA",
    ):

        reasons.append(
            "A tendência técnica permanece negativa."
        )

    elif trend == "CORREÇÃO":

        reasons.append(
            "O ativo passa por uma correção dentro da tendência."
        )

    # ------------------------------------------------------
    # RSI
    # ------------------------------------------------------

    rsi = safe_float(
        indicators.get(
            "rsi"
        )
    )

    if rsi is not None:

        if rsi >= 70:

            reasons.append(
                f"RSI em {rsi:.1f}, indicando possível sobrecompra."
            )

        elif rsi <= 30:

            reasons.append(
                f"RSI em {rsi:.1f}, indicando região de sobrevenda."
            )

        elif rsi >= 50:

            reasons.append(
                f"RSI em {rsi:.1f}, com momentum positivo."
            )

        else:

            reasons.append(
                f"RSI em {rsi:.1f}, com momentum mais fraco."
            )

    # ------------------------------------------------------
    # MÉDIAS
    # ------------------------------------------------------

    distance_ma21 = safe_float(
        indicators.get(
            "distance_ma21"
        )
    )

    if distance_ma21 is not None:

        if distance_ma21 > 0:

            reasons.append(
                "O preço está acima da média móvel de 21 períodos."
            )

        else:

            reasons.append(
                "O preço está abaixo da média móvel de 21 períodos."
            )

    distance_ma200 = safe_float(
        indicators.get(
            "distance_ma200"
        )
    )

    if distance_ma200 is not None:

        if distance_ma200 > 0:

            reasons.append(
                "O preço está acima da média móvel de 200 períodos."
            )

        else:

            reasons.append(
                "O preço está abaixo da média móvel de 200 períodos."
            )

    # ------------------------------------------------------
    # VOLUME
    # ------------------------------------------------------

    relative_volume = safe_float(
        indicators.get(
            "relative_volume"
        )
    )

    if relative_volume is not None:

        if relative_volume >= 1.5:

            reasons.append(
                "O volume negociado está significativamente acima da média."
            )

        elif relative_volume < 0.7:

            reasons.append(
                "O volume negociado está abaixo da média."
            )

    # ------------------------------------------------------
    # FUNDAMENTOS
    # ------------------------------------------------------

    if fundamental_score >= 70:

        reasons.append(
            "A avaliação fundamentalista apresenta resultado favorável."
        )

    elif fundamental_score < 45:

        reasons.append(
            "Os fundamentos apresentam pontos de atenção."
        )

    # ------------------------------------------------------
    # RISCO
    # ------------------------------------------------------

    risk = safe_upper(
        risk
    )

    if risk in (
        "ALTO",
        "MUITO ALTO",
    ):

        reasons.append(
            f"O nível de risco atual foi classificado como {risk}."
        )

    elif risk == "BAIXO":

        reasons.append(
            "O perfil de risco técnico atual é relativamente controlado."
        )

    # ------------------------------------------------------
    # SCORE INTEGRADO
    # ------------------------------------------------------

    if integrated_score >= 80:

        reasons.append(
            "Os fatores técnicos e fundamentalistas apresentam forte convergência positiva."
        )

    elif integrated_score < 45:

        reasons.append(
            "O conjunto dos fatores apresenta baixa convicção positiva."
        )

    # ------------------------------------------------------
    # EVITA DUPLICADOS
    # ------------------------------------------------------

    unique_reasons = []

    for reason in reasons:

        if reason not in unique_reasons:

            unique_reasons.append(
                reason
            )

    return unique_reasons[:8]


# ==========================================================
# RESUMO EXECUTIVO
# ==========================================================

def generate_executive_summary(
    asset,
    current_price,
    technical_score,
    technical_classification,
    fundamental_score,
    fundamental_classification,
    integrated_score,
    integrated_classification,
    trend,
    risk,
    recommendation,
):
    """
    Gera o resumo executivo da análise.
    """

    asset = str(
        asset or "ATIVO"
    ).upper()

    technical_score = clamp(
        technical_score
    )

    fundamental_score = clamp(
        fundamental_score
    )

    integrated_score = clamp(
        integrated_score
    )

    price = safe_float(
        current_price
    )

    if price is not None:

        price_text = (
            f" O último preço identificado foi "
            f"{price:,.2f}."
        )

    else:

        price_text = ""

    return (
        f"O ativo {asset} apresenta Score Integrado de "
        f"{integrated_score:.0f}/100, classificado como "
        f"{integrated_classification}. "
        f"O Score Técnico é de {technical_score:.0f}/100 "
        f"({technical_classification}) e o Score Fundamentalista "
        f"é de {fundamental_score:.0f}/100 "
        f"({fundamental_classification}). "
        f"A tendência atual é {trend} e o nível de risco foi "
        f"classificado como {risk}. "
        f"A decisão executiva indicada pelo modelo é "
        f"{recommendation}.{price_text}"
    )


# ==========================================================
# MOTOR PRINCIPAL
# ==========================================================

def analyze_asset(
    data,
    asset=None,
    technical_weight=0.50,
    fundamental_weight=0.50,
):
    """
    Função principal do motor de análise.

    Entrada esperada:

    {
        "asset": "PETR4.SA",
        "price": 35.50,
        "ma21": 34.80,
        "ma200": 32.10,
        "rsi": 58.20,
        "volatility": 0.25,
        "indicators": {...},
        "fundamentals": {...}
    }

    Também mantém compatibilidade com a estrutura
    utilizada nas versões anteriores.
    """

    # ------------------------------------------------------
    # VALIDAÇÃO
    # ------------------------------------------------------

    if not isinstance(
        data,
        dict,
    ):

        data = {}

    # ------------------------------------------------------
    # ATIVO
    # ------------------------------------------------------

    if asset is None:

        asset = data.get(
            "asset",
            "ATIVO",
        )

    asset = str(
        asset or "ATIVO"
    ).upper()

    # ------------------------------------------------------
    # INDICADORES
    # ------------------------------------------------------

    indicators = get_indicators(
        data
    )

    # Cria cópia para evitar modificar a entrada original
    indicators = dict(
        indicators
    )

    # ------------------------------------------------------
    # COMPATIBILIDADE COM app.py
    # ------------------------------------------------------

    compatibility_keys = [
        "price",
        "current_price",
        "ma21",
        "ma200",
        "rsi",
        "volatility",
        "annual_volatility",
        "short_trend",
        "long_trend",
        "distance_ma21",
        "distance_ma200",
        "relative_volume",
        "range_position",
    ]

    for key in compatibility_keys:

        if (
            key not in indicators
            and key in data
        ):

            indicators[key] = data.get(
                key
            )

    # ------------------------------------------------------
    # FUNDAMENTOS
    # ------------------------------------------------------

    fundamentals = get_fundamentals(
        data
    )

    # ------------------------------------------------------
    # PREÇO
    # ------------------------------------------------------

    current_price = safe_float(
        data.get(
            "price",
            data.get(
                "current_price",
                indicators.get(
                    "price",
                    indicators.get(
                        "current_price"
                    ),
                ),
            ),
        )
    )

    # ======================================================
    # CALCULA SCORES
    # ======================================================

    scores = calculate_investia_scores(
        indicators=indicators,
        fundamentals=fundamentals,
        technical_weight=technical_weight,
        fundamental_weight=fundamental_weight,
    )

    # ------------------------------------------------------
    # SCORE TÉCNICO
    # ------------------------------------------------------

    technical_score = clamp(
        scores.get(
            "technical_score",
            50,
        )
    )

    technical_classification = (
        scores.get(
            "technical_classification",
            "NEUTRO",
        )
    )

    technical_signal = scores.get(
        "technical_signal",
        "NEUTRO",
    )

    technical_breakdown = scores.get(
        "technical_breakdown",
        {},
    )

    # ------------------------------------------------------
    # SCORE FUNDAMENTALISTA
    # ------------------------------------------------------

    fundamental_score = clamp(
        scores.get(
            "fundamental_score",
            50,
        )
    )

    fundamental_classification = (
        scores.get(
            "fundamental_classification",
            "NEUTRO",
        )
    )

    fundamental_signal = scores.get(
        "fundamental_signal",
        "NEUTRO",
    )

    fundamental_breakdown = scores.get(
        "fundamental_breakdown",
        {},
    )

    # ------------------------------------------------------
    # SCORE INTEGRADO
    # ------------------------------------------------------

    integrated_score = clamp(
        scores.get(
            "integrated_score",
            50,
        )
    )

    integrated_classification = (
        scores.get(
            "integrated_classification",
            "NEUTRO",
        )
    )

    integrated_signal = scores.get(
        "integrated_signal",
        "NEUTRO",
    )

    integrated_breakdown = scores.get(
        "integrated_breakdown",
        {},
    )

    # ======================================================
    # TENDÊNCIA
    # ======================================================

    trend = determine_trend(
        indicators
    )

    # ======================================================
    # RISCO
    # ======================================================

    risk = determine_risk(
        indicators=indicators,
        integrated_score=integrated_score,
    )

    # ======================================================
    # RECOMENDAÇÃO
    # ======================================================

    recommendation = determine_recommendation(
        integrated_score=integrated_score,
        technical_score=technical_score,
        fundamental_score=fundamental_score,
        trend=trend,
        risk=risk,
    )

    # ======================================================
    # SINAL QUALIFICADO
    # ======================================================

    qualified_signal = determine_qualified_signal(
        integrated_score=integrated_score,
        technical_score=technical_score,
        fundamental_score=fundamental_score,
        trend=trend,
        risk=risk,
    )

    # ======================================================
    # ÍCONE
    # ======================================================

    signal_icon = get_signal_icon(
        integrated_signal
    )

    # ======================================================
    # FATORES
    # ======================================================

    reasons = generate_reasons(
        indicators=indicators,
        fundamentals=fundamentals,
        technical_score=technical_score,
        fundamental_score=fundamental_score,
        integrated_score=integrated_score,
        trend=trend,
        risk=risk,
    )

    # ======================================================
    # RESUMO EXECUTIVO
    # ======================================================

    executive_summary = generate_executive_summary(
        asset=asset,
        current_price=current_price,
        technical_score=technical_score,
        technical_classification=technical_classification,
        fundamental_score=fundamental_score,
        fundamental_classification=fundamental_classification,
        integrated_score=integrated_score,
        integrated_classification=integrated_classification,
        trend=trend,
        risk=risk,
        recommendation=recommendation,
    )

    # ======================================================
    # RETORNO CONSOLIDADO
    # ======================================================

    return {

        # --------------------------------------------------
        # IDENTIFICAÇÃO
        # --------------------------------------------------

        "asset": asset,

        "price": current_price,

        # --------------------------------------------------
        # SCORE TÉCNICO
        # --------------------------------------------------

        "technical_score": technical_score,

        "technical_classification": technical_classification,

        "technical_signal": technical_signal,

        "technical_breakdown": technical_breakdown,

        # --------------------------------------------------
        # SCORE FUNDAMENTALISTA
        # --------------------------------------------------

        "fundamental_score": fundamental_score,

        "fundamental_classification": fundamental_classification,

        "fundamental_signal": fundamental_signal,

        "fundamental_breakdown": fundamental_breakdown,

        # --------------------------------------------------
        # SCORE INTEGRADO
        # --------------------------------------------------

        "integrated_score": integrated_score,

        "integrated_classification": integrated_classification,

        "integrated_signal": integrated_signal,

        "integrated_breakdown": integrated_breakdown,

        # --------------------------------------------------
        # COMPATIBILIDADE COM VERSÕES ANTERIORES
        # --------------------------------------------------

        "score": integrated_score,

        "classification": integrated_classification,

        "signal": integrated_signal,

        "breakdown": integrated_breakdown,

        # --------------------------------------------------
        # PESOS
        # --------------------------------------------------

        "technical_weight": scores.get(
            "technical_weight",
            technical_weight,
        ),

        "fundamental_weight": scores.get(
            "fundamental_weight",
            fundamental_weight,
        ),

        # --------------------------------------------------
        # DECISÃO EXECUTIVA
        # --------------------------------------------------

        "trend": trend,

        "risk": risk,

        "recommendation": recommendation,

        "qualified_signal": qualified_signal,

        "signal_icon": signal_icon,

        # --------------------------------------------------
        # EXPLICABILIDADE
        # --------------------------------------------------

        "reasons": reasons,

        "executive_summary": executive_summary,

        # --------------------------------------------------
        # DADOS DE APOIO
        # --------------------------------------------------

        "indicators": indicators,

        "fundamentals": fundamentals,
    }


# ==========================================================
# TESTE LOCAL
# ==========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("InvestIA PRO")
    print("Analysis.py")
    print("Fase 3.0.7")
    print("=" * 60)

    test_data = {

        "asset": "PETR4.SA",

        "price": 38.50,

        "ma21": 37.80,

        "ma200": 35.20,

        "rsi": 58.40,

        "volatility": 0.022,

        "short_trend": "ALTA",

        "long_trend": "ALTA",

        "distance_ma21": 0.0185,

        "distance_ma200": 0.0937,

        "relative_volume": 1.20,

        "range_position": 0.72,

        "annual_volatility": 0.35,

        "fundamentals": {

            "trailingPE": 8.50,

            "priceToBook": 1.20,

            "returnOnEquity": 0.18,

            "profitMargins": 0.15,

            "debtToEbitda": 1.80,

            "revenueGrowth": 0.12,

            "dividendYield": 0.06,
        },
    }

    result = analyze_asset(
        data=test_data,
        asset="PETR4.SA",
        technical_weight=0.50,
        fundamental_weight=0.50,
    )

    print()

    print(
        "SCORE TÉCNICO:",
        round(
            result["technical_score"],
            2,
        ),
    )

    print(
        "CLASSIFICAÇÃO:",
        result["technical_classification"],
    )

    print()

    print(
        "SCORE FUNDAMENTALISTA:",
        round(
            result["fundamental_score"],
            2,
        ),
    )

    print(
        "CLASSIFICAÇÃO:",
        result["fundamental_classification"],
    )

    print()

    print(
        "SCORE INTEGRADO:",
        round(
            result["integrated_score"],
            2,
        ),
    )

    print(
        "CLASSIFICAÇÃO:",
        result["integrated_classification"],
    )

    print()

    print(
        "TENDÊNCIA:",
        result["trend"],
    )

    print(
        "RISCO:",
        result["risk"],
    )

    print(
        "RECOMENDAÇÃO:",
        result["recommendation"],
    )

    print()

    print(
        "RESUMO EXECUTIVO:"
    )

    print(
        result["executive_summary"]
    )
