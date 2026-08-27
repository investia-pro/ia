"""
InvestIA PRO
Motor de Scores

Versão: v3.1.3
Fase Final: 3.1.3

Responsabilidades:
- Score Técnico
- Score Fundamentalista
- Score Integrado
- Classificação dos Scores
- Geração de sinais
- Explicabilidade do cálculo

Compatível com:
- market.py Fase 3.0.7
- indicators.py Fase 3.0.7
- analysis.py Fase 3.0.6+
- app.py Fase 3.0.6+
"""

import math


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
    except (TypeError, ValueError):
        return default

    if not math.isfinite(value):
        return default

    return value


def clamp(value, minimum=0, maximum=100):
    """
    Limita um valor dentro de um intervalo.
    """

    value = safe_float(value, minimum)

    return max(
        minimum,
        min(maximum, value),
    )


def get_nested_value(data, key, default=None):
    """
    Obtém um valor de dicionário com segurança.
    """

    if not isinstance(data, dict):
        return default

    return data.get(key, default)


def create_breakdown_item(
    points=0,
    signal="NEUTRO",
    reason="Não disponível.",
    value=None,
    weight=None,
):
    """
    Cria um item padronizado de explicabilidade.
    """

    return {
        "points": safe_float(points, 0),
        "signal": signal,
        "reason": reason,
        "value": value,
        "weight": weight,
    }


# ==========================================================
# CLASSIFICAÇÃO
# ==========================================================

def classify_score(score):
    """
    Classifica o Score entre 0 e 100.
    """

    score = clamp(score)

    if score >= 80:
        return "MUITO FORTE"

    if score >= 65:
        return "POSITIVO"

    if score >= 45:
        return "NEUTRO"

    if score >= 30:
        return "NEGATIVO"

    return "MUITO FRACO"


def get_signal_from_score(score):
    """
    Retorna um sinal operacional baseado no Score.
    """

    score = clamp(score)

    if score >= 80:
        return "COMPRA FORTE"

    if score >= 65:
        return "COMPRA"

    if score >= 45:
        return "NEUTRO"

    if score >= 30:
        return "CAUTELA"

    return "VENDA"


def get_signal_icon(signal):
    """
    Retorna o ícone visual do sinal.
    """

    signal = str(signal or "").upper()

    icons = {
        "COMPRA FORTE": "🚀",
        "COMPRA": "🟢",
        "NEUTRO": "⚪",
        "CAUTELA": "🟠",
        "VENDA": "🔴",
    }

    return icons.get(
        signal,
        "⚪",
    )


# ==========================================================
# SCORE TÉCNICO
# ==========================================================

def calculate_technical_score(indicators):
    """
    Calcula o Score Técnico.

    Componentes:

    1. Tendência de curto prazo      -> 15 pontos
    2. Tendência de longo prazo      -> 20 pontos
    3. Preço vs MA21                 -> 10 pontos
    4. Preço vs MA200                -> 15 pontos
    5. RSI                           -> 15 pontos
    6. Volume relativo               -> 10 pontos
    7. Posição no range              -> 5 pontos
    8. Volatilidade                  -> 10 pontos

    Total: 100 pontos
    """

    if not isinstance(indicators, dict):
        return {
            "score": 0,
            "classification": "MUITO FRACO",
            "signal": "VENDA",
            "breakdown": {},
        }

    breakdown = {}

    total_score = 0

    # ======================================================
    # 1. TENDÊNCIA CURTO PRAZO
    # ======================================================

    short_trend = str(
        indicators.get(
            "short_trend",
            "N/D",
        )
    ).upper()

    short_points = 0
    short_signal = "NEUTRO"

    if short_trend == "FORTE ALTA":
        short_points = 15
        short_signal = "POSITIVO"
        short_reason = "Tendência de curto prazo fortemente positiva."

    elif short_trend == "ALTA":
        short_points = 11
        short_signal = "POSITIVO"
        short_reason = "Tendência de curto prazo positiva."

    elif short_trend == "NEUTRA":
        short_points = 7
        short_signal = "NEUTRO"
        short_reason = "Tendência de curto prazo neutra."

    elif short_trend == "BAIXA":
        short_points = 3
        short_signal = "NEGATIVO"
        short_reason = "Tendência de curto prazo negativa."

    elif short_trend == "FORTE BAIXA":
        short_points = 0
        short_signal = "NEGATIVO"
        short_reason = "Tendência de curto prazo fortemente negativa."

    else:
        short_points = 7
        short_signal = "NEUTRO"
        short_reason = "Dados insuficientes para classificar a tendência de curto prazo."

    total_score += short_points

    breakdown["short_trend"] = create_breakdown_item(
        points=short_points,
        signal=short_signal,
        reason=short_reason,
        value=short_trend,
        weight=15,
    )

    # ======================================================
    # 2. TENDÊNCIA LONGO PRAZO
    # ======================================================

    long_trend = str(
        indicators.get(
            "long_trend",
            "N/D",
        )
    ).upper()

    long_points = 0
    long_signal = "NEUTRO"

    if long_trend == "FORTE ALTA":
        long_points = 20
        long_signal = "POSITIVO"
        long_reason = "Tendência estrutural de longo prazo fortemente positiva."

    elif long_trend == "ALTA":
        long_points = 15
        long_signal = "POSITIVO"
        long_reason = "Tendência estrutural de longo prazo positiva."

    elif long_trend == "NEUTRA":
        long_points = 10
        long_signal = "NEUTRO"
        long_reason = "Tendência estrutural de longo prazo neutra."

    elif long_trend == "BAIXA":
        long_points = 5
        long_signal = "NEGATIVO"
        long_reason = "Tendência estrutural de longo prazo negativa."

    elif long_trend == "FORTE BAIXA":
        long_points = 0
        long_signal = "NEGATIVO"
        long_reason = "Tendência estrutural de longo prazo fortemente negativa."

    else:
        long_points = 10
        long_signal = "NEUTRO"
        long_reason = "Dados insuficientes para classificar a tendência de longo prazo."

    total_score += long_points

    breakdown["long_trend"] = create_breakdown_item(
        points=long_points,
        signal=long_signal,
        reason=long_reason,
        value=long_trend,
        weight=20,
    )

    # ======================================================
    # 3. DISTÂNCIA MA21
    # ======================================================

    distance_ma21 = safe_float(
        indicators.get("distance_ma21")
    )

    ma21_points = 0
    ma21_signal = "NEUTRO"

    if distance_ma21 is None:
        ma21_points = 5
        ma21_reason = "Distância em relação à MA21 não disponível."

    elif distance_ma21 >= 0.05:
        ma21_points = 10
        ma21_signal = "POSITIVO"
        ma21_reason = "Preço significativamente acima da MA21."

    elif distance_ma21 > 0:
        ma21_points = 8
        ma21_signal = "POSITIVO"
        ma21_reason = "Preço acima da MA21."

    elif distance_ma21 >= -0.03:
        ma21_points = 5
        ma21_reason = "Preço próximo da MA21."

    elif distance_ma21 >= -0.08:
        ma21_points = 2
        ma21_signal = "NEGATIVO"
        ma21_reason = "Preço abaixo da MA21."

    else:
        ma21_points = 0
        ma21_signal = "NEGATIVO"
        ma21_reason = "Preço significativamente abaixo da MA21."

    total_score += ma21_points

    breakdown["distance_ma21"] = create_breakdown_item(
        points=ma21_points,
        signal=ma21_signal,
        reason=ma21_reason,
        value=distance_ma21,
        weight=10,
    )

    # ======================================================
    # 4. DISTÂNCIA MA200
    # ======================================================

    distance_ma200 = safe_float(
        indicators.get("distance_ma200")
    )

    ma200_points = 0
    ma200_signal = "NEUTRO"

    if distance_ma200 is None:
        ma200_points = 8
        ma200_reason = "Distância em relação à MA200 não disponível."

    elif distance_ma200 >= 0.10:
        ma200_points = 15
        ma200_signal = "POSITIVO"
        ma200_reason = "Preço significativamente acima da MA200."

    elif distance_ma200 > 0:
        ma200_points = 12
        ma200_signal = "POSITIVO"
        ma200_reason = "Preço acima da MA200."

    elif distance_ma200 >= -0.05:
        ma200_points = 8
        ma200_reason = "Preço próximo da MA200."

    elif distance_ma200 >= -0.15:
        ma200_points = 4
        ma200_signal = "NEGATIVO"
        ma200_reason = "Preço abaixo da MA200."

    else:
        ma200_points = 0
        ma200_signal = "NEGATIVO"
        ma200_reason = "Preço significativamente abaixo da MA200."

    total_score += ma200_points

    breakdown["distance_ma200"] = create_breakdown_item(
        points=ma200_points,
        signal=ma200_signal,
        reason=ma200_reason,
        value=distance_ma200,
        weight=15,
    )

    # ======================================================
    # 5. RSI
    # ======================================================

    rsi = safe_float(
        indicators.get("rsi")
    )

    rsi_points = 0
    rsi_signal = "NEUTRO"

    if rsi is None:
        rsi_points = 7
        rsi_reason = "RSI não disponível."

    elif 50 <= rsi <= 65:
        rsi_points = 15
        rsi_signal = "POSITIVO"
        rsi_reason = "RSI positivo sem indicar sobrecompra extrema."

    elif 40 <= rsi < 50:
        rsi_points = 9
        rsi_reason = "RSI em zona neutra com viés moderadamente fraco."

    elif 65 < rsi <= 70:
        rsi_points = 11
        rsi_signal = "POSITIVO"
        rsi_reason = "RSI forte, porém próximo da zona de sobrecompra."

    elif 30 <= rsi < 40:
        rsi_points = 5
        rsi_signal = "NEGATIVO"
        rsi_reason = "RSI fraco e próximo de sobrevenda."

    elif rsi > 70:
        rsi_points = 8
        rsi_signal = "CAUTELA"
        rsi_reason = "RSI em sobrecompra, aumentando o risco de correção."

    else:
        rsi_points = 6
        rsi_signal = "NEUTRO"
        rsi_reason = "RSI em sobrevenda, podendo indicar pressão vendedora excessiva."

    total_score += rsi_points

    breakdown["rsi"] = create_breakdown_item(
        points=rsi_points,
        signal=rsi_signal,
        reason=rsi_reason,
        value=rsi,
        weight=15,
    )

    # ======================================================
    # 6. VOLUME RELATIVO
    # ======================================================

    relative_volume = safe_float(
        indicators.get("relative_volume")
    )

    volume_points = 0
    volume_signal = "NEUTRO"

    if relative_volume is None:
        volume_points = 5
        volume_reason = "Volume relativo não disponível."

    elif relative_volume >= 1.50:
        volume_points = 10
        volume_signal = "POSITIVO"
        volume_reason = "Volume significativamente acima da média."

    elif relative_volume >= 1.15:
        volume_points = 8
        volume_signal = "POSITIVO"
        volume_reason = "Volume acima da média."

    elif relative_volume >= 0.85:
        volume_points = 6
        volume_reason = "Volume dentro da faixa normal."

    elif relative_volume >= 0.50:
        volume_points = 3
        volume_signal = "NEGATIVO"
        volume_reason = "Volume abaixo da média."

    else:
        volume_points = 1
        volume_signal = "NEGATIVO"
        volume_reason = "Volume muito abaixo da média."

    total_score += volume_points

    breakdown["relative_volume"] = create_breakdown_item(
        points=volume_points,
        signal=volume_signal,
        reason=volume_reason,
        value=relative_volume,
        weight=10,
    )

    # ======================================================
    # 7. POSIÇÃO NO RANGE
    # ======================================================

    range_position = safe_float(
        indicators.get("range_position")
    )

    range_points = 0
    range_signal = "NEUTRO"

    if range_position is None:
        range_points = 2
        range_reason = "Posição no range não disponível."

    elif range_position >= 0.80:
        range_points = 5
        range_signal = "POSITIVO"
        range_reason = "Preço operando próximo das máximas do período."

    elif range_position >= 0.60:
        range_points = 4
        range_signal = "POSITIVO"
        range_reason = "Preço localizado na faixa superior do período."

    elif range_position >= 0.40:
        range_points = 3
        range_reason = "Preço localizado na região intermediária do período."

    elif range_position >= 0.20:
        range_points = 2
        range_signal = "NEGATIVO"
        range_reason = "Preço localizado na faixa inferior do período."

    else:
        range_points = 1
        range_signal = "NEGATIVO"
        range_reason = "Preço operando próximo das mínimas do período."

    total_score += range_points

    breakdown["range_position"] = create_breakdown_item(
        points=range_points,
        signal=range_signal,
        reason=range_reason,
        value=range_position,
        weight=5,
    )

    # ======================================================
    # 8. VOLATILIDADE
    # ======================================================

    annual_volatility = safe_float(
        indicators.get("annual_volatility")
    )

    if annual_volatility is None:
        annual_volatility = safe_float(
            indicators.get("volatility")
        )

        if annual_volatility is not None:
            annual_volatility = annual_volatility * (
                252 ** 0.5
            )

    volatility_points = 0
    volatility_signal = "NEUTRO"

    if annual_volatility is None:
        volatility_points = 5
        volatility_reason = "Volatilidade não disponível."

    elif annual_volatility <= 0.20:
        volatility_points = 10
        volatility_signal = "POSITIVO"
        volatility_reason = "Volatilidade baixa."

    elif annual_volatility <= 0.35:
        volatility_points = 8
        volatility_reason = "Volatilidade moderada."

    elif annual_volatility <= 0.50:
        volatility_points = 5
        volatility_signal = "CAUTELA"
        volatility_reason = "Volatilidade elevada."

    elif annual_volatility <= 0.75:
        volatility_points = 2
        volatility_signal = "NEGATIVO"
        volatility_reason = "Volatilidade alta."

    else:
        volatility_points = 0
        volatility_signal = "NEGATIVO"
        volatility_reason = "Volatilidade extremamente elevada."

    total_score += volatility_points

    breakdown["volatility"] = create_breakdown_item(
        points=volatility_points,
        signal=volatility_signal,
        reason=volatility_reason,
        value=annual_volatility,
        weight=10,
    )

    # ======================================================
    # RESULTADO FINAL
    # ======================================================

    final_score = clamp(total_score)

    classification = classify_score(
        final_score
    )

    signal = get_signal_from_score(
        final_score
    )

    breakdown["score"] = {
        "points": final_score,
        "signal": signal,
        "reason": "Resultado consolidado do Score Técnico.",
    }

    return {
        "score": final_score,
        "classification": classification,
        "signal": signal,
        "breakdown": breakdown,
    }


# ==========================================================
# SCORE FUNDAMENTALISTA
# ==========================================================

def calculate_fundamental_score(fundamentals):
    """
    Calcula o Score Fundamentalista.

    Indicadores utilizados quando disponíveis:

    - P/L
    - P/VP
    - ROE
    - Margem líquida
    - Dívida / EBITDA
    - Crescimento da receita
    - Dividend Yield

    Quando um indicador não está disponível,
    ele não recebe pontuação arbitrária positiva.
    A pontuação é redistribuída entre os
    indicadores efetivamente disponíveis.
    """

    if not isinstance(fundamentals, dict):
        return {
            "score": 50,
            "classification": "NEUTRO",
            "signal": "NEUTRO",
            "breakdown": {},
        }

    breakdown = {}

    metrics = []

    # ------------------------------------------------------
    # P/L
    # ------------------------------------------------------

    pe_ratio = safe_float(
        fundamentals.get(
            "trailingPE",
            fundamentals.get("pe_ratio"),
        )
    )

    if pe_ratio is not None and pe_ratio > 0:

        if pe_ratio <= 8:
            raw_score = 100
            reason = "P/L baixo em relação aos lucros."

        elif pe_ratio <= 15:
            raw_score = 80
            reason = "P/L considerado atrativo."

        elif pe_ratio <= 25:
            raw_score = 60
            reason = "P/L em faixa moderada."

        elif pe_ratio <= 40:
            raw_score = 35
            reason = "P/L elevado."

        else:
            raw_score = 15
            reason = "P/L muito elevado."

        metrics.append(
            {
                "key": "pe_ratio",
                "name": "P/L",
                "value": pe_ratio,
                "weight": 15,
                "score": raw_score,
                "reason": reason,
            }
        )

    # ------------------------------------------------------
    # P/VP
    # ------------------------------------------------------

    pb_ratio = safe_float(
        fundamentals.get(
            "priceToBook",
            fundamentals.get("pb_ratio"),
        )
    )

    if pb_ratio is not None and pb_ratio > 0:

        if pb_ratio <= 1:
            raw_score = 100
            reason = "P/VP igual ou inferior a 1."

        elif pb_ratio <= 2:
            raw_score = 75
            reason = "P/VP em faixa moderada."

        elif pb_ratio <= 4:
            raw_score = 50
            reason = "P/VP elevado."

        else:
            raw_score = 25
            reason = "P/VP muito elevado."

        metrics.append(
            {
                "key": "pb_ratio",
                "name": "P/VP",
                "value": pb_ratio,
                "weight": 10,
                "score": raw_score,
                "reason": reason,
            }
        )

    # ------------------------------------------------------
    # ROE
    # ------------------------------------------------------

    roe = safe_float(
        fundamentals.get(
            "returnOnEquity",
            fundamentals.get("roe"),
        )
    )

    if roe is not None:

        if abs(roe) <= 1:
            roe_percent = roe * 100
        else:
            roe_percent = roe

        if roe_percent >= 20:
            raw_score = 100
            reason = "ROE muito elevado."

        elif roe_percent >= 15:
            raw_score = 85
            reason = "ROE forte."

        elif roe_percent >= 10:
            raw_score = 65
            reason = "ROE satisfatório."

        elif roe_percent >= 5:
            raw_score = 45
            reason = "ROE moderado."

        elif roe_percent >= 0:
            raw_score = 25
            reason = "ROE baixo."

        else:
            raw_score = 0
            reason = "ROE negativo."

        metrics.append(
            {
                "key": "roe",
                "name": "ROE",
                "value": roe,
                "weight": 20,
                "score": raw_score,
                "reason": reason,
            }
        )

    # ------------------------------------------------------
    # MARGEM LÍQUIDA
    # ------------------------------------------------------

    net_margin = safe_float(
        fundamentals.get(
            "profitMargins",
            fundamentals.get("net_margin"),
        )
    )

    if net_margin is not None:

        if abs(net_margin) <= 1:
            margin_percent = net_margin * 100
        else:
            margin_percent = net_margin

        if margin_percent >= 20:
            raw_score = 100
            reason = "Margem líquida muito elevada."

        elif margin_percent >= 10:
            raw_score = 80
            reason = "Margem líquida forte."

        elif margin_percent >= 5:
            raw_score = 60
            reason = "Margem líquida positiva."

        elif margin_percent >= 0:
            raw_score = 35
            reason = "Margem líquida baixa."

        else:
            raw_score = 0
            reason = "Empresa apresenta prejuízo."

        metrics.append(
            {
                "key": "net_margin",
                "name": "Margem Líquida",
                "value": net_margin,
                "weight": 15,
                "score": raw_score,
                "reason": reason,
            }
        )

    # ------------------------------------------------------
    # DÍVIDA / EBITDA
    # ------------------------------------------------------

    debt_to_ebitda = safe_float(
        fundamentals.get(
            "debtToEbitda",
            fundamentals.get("debt_to_ebitda"),
        )
    )

    if debt_to_ebitda is not None:

        if debt_to_ebitda <= 1:
            raw_score = 100
            reason = "Endividamento baixo."

        elif debt_to_ebitda <= 2:
            raw_score = 80
            reason = "Endividamento controlado."

        elif debt_to_ebitda <= 3:
            raw_score = 60
            reason = "Endividamento moderado."

        elif debt_to_ebitda <= 4:
            raw_score = 35
            reason = "Endividamento elevado."

        else:
            raw_score = 10
            reason = "Endividamento muito elevado."

        metrics.append(
            {
                "key": "debt_to_ebitda",
                "name": "Dívida / EBITDA",
                "value": debt_to_ebitda,
                "weight": 15,
                "score": raw_score,
                "reason": reason,
            }
        )

    # ------------------------------------------------------
    # CRESCIMENTO DA RECEITA
    # ------------------------------------------------------

    revenue_growth = safe_float(
        fundamentals.get(
            "revenueGrowth",
            fundamentals.get("revenue_growth"),
        )
    )

    if revenue_growth is not None:

        if abs(revenue_growth) <= 1:
            growth_percent = revenue_growth * 100
        else:
            growth_percent = revenue_growth

        if growth_percent >= 20:
            raw_score = 100
            reason = "Crescimento de receita muito forte."

        elif growth_percent >= 10:
            raw_score = 85
            reason = "Crescimento de receita forte."

        elif growth_percent >= 5:
            raw_score = 70
            reason = "Crescimento de receita positivo."

        elif growth_percent >= 0:
            raw_score = 50
            reason = "Receita estável ou com crescimento limitado."

        elif growth_percent >= -10:
            raw_score = 25
            reason = "Receita em retração moderada."

        else:
            raw_score = 0
            reason = "Receita em forte retração."

        metrics.append(
            {
                "key": "revenue_growth",
                "name": "Crescimento da Receita",
                "value": revenue_growth,
                "weight": 15,
                "score": raw_score,
                "reason": reason,
            }
        )

    # ------------------------------------------------------
    # DIVIDEND YIELD
    # ------------------------------------------------------

    dividend_yield = safe_float(
        fundamentals.get(
            "dividendYield",
            fundamentals.get("dividend_yield"),
        )
    )

    if dividend_yield is not None:

        if abs(dividend_yield) <= 1:
            dy_percent = dividend_yield * 100
        else:
            dy_percent = dividend_yield

        if dy_percent >= 8:
            raw_score = 100
            reason = "Dividend Yield elevado."

        elif dy_percent >= 5:
            raw_score = 80
            reason = "Dividend Yield atrativo."

        elif dy_percent >= 3:
            raw_score = 65
            reason = "Dividend Yield moderado."

        elif dy_percent > 0:
            raw_score = 45
            reason = "Dividend Yield baixo."

        else:
            raw_score = 20
            reason = "Não há Dividend Yield relevante."

        metrics.append(
            {
                "key": "dividend_yield",
                "name": "Dividend Yield",
                "value": dividend_yield,
                "weight": 10,
                "score": raw_score,
                "reason": reason,
            }
        )

    # ======================================================
    # RESULTADO FUNDAMENTALISTA
    # ======================================================

    if not metrics:

        return {
            "score": 50,
            "classification": "NEUTRO",
            "signal": "NEUTRO",
            "breakdown": {
                "data_availability": create_breakdown_item(
                    points=50,
                    signal="NEUTRO",
                    reason=(
                        "Dados fundamentalistas insuficientes "
                        "para uma avaliação completa."
                    ),
                    value=None,
                    weight=0,
                )
            },
        }

    total_weight = sum(
        metric["weight"]
        for metric in metrics
    )

    weighted_score = sum(
        metric["score"] * metric["weight"]
        for metric in metrics
    ) / total_weight

    final_score = clamp(
        weighted_score
    )

    for metric in metrics:

        normalized_points = (
            metric["score"]
            * metric["weight"]
            / total_weight
        )

        if metric["score"] >= 70:
            metric_signal = "POSITIVO"

        elif metric["score"] >= 45:
            metric_signal = "NEUTRO"

        else:
            metric_signal = "NEGATIVO"

        breakdown[
            metric["key"]
        ] = create_breakdown_item(
            points=normalized_points,
            signal=metric_signal,
            reason=metric["reason"],
            value=metric["value"],
            weight=metric["weight"],
        )

    classification = classify_score(
        final_score
    )

    signal = get_signal_from_score(
        final_score
    )

    breakdown["score"] = {
        "points": final_score,
        "signal": signal,
        "reason": (
            "Resultado consolidado do "
            "Score Fundamentalista."
        ),
    }

    return {
        "score": final_score,
        "classification": classification,
        "signal": signal,
        "breakdown": breakdown,
    }


# ==========================================================
# SCORE INTEGRADO
# ==========================================================

def calculate_integrated_score(
    technical_score,
    fundamental_score,
    technical_weight=0.50,
    fundamental_weight=0.50,
):
    """
    Calcula o Score Integrado.

    O usuário pode definir os pesos no app.py.

    Exemplo:

    technical_weight = 0.60
    fundamental_weight = 0.40
    """

    technical_score = clamp(
        technical_score
    )

    fundamental_score = clamp(
        fundamental_score
    )

    technical_weight = safe_float(
        technical_weight,
        0.50,
    )

    fundamental_weight = safe_float(
        fundamental_weight,
        0.50,
    )

    # Evita pesos negativos
    technical_weight = max(
        0,
        technical_weight,
    )

    fundamental_weight = max(
        0,
        fundamental_weight,
    )

    total_weight = (
        technical_weight
        + fundamental_weight
    )

    # Fallback seguro
    if total_weight <= 0:

        technical_weight = 0.50
        fundamental_weight = 0.50
        total_weight = 1

    # Normalização
    technical_weight = (
        technical_weight
        / total_weight
    )

    fundamental_weight = (
        fundamental_weight
        / total_weight
    )

    integrated_score = (
        technical_score
        * technical_weight
    ) + (
        fundamental_score
        * fundamental_weight
    )

    integrated_score = clamp(
        integrated_score
    )

    classification = classify_score(
        integrated_score
    )

    signal = get_signal_from_score(
        integrated_score
    )

    breakdown = {

        "technical_score": create_breakdown_item(
            points=technical_score * technical_weight,
            signal=get_signal_from_score(
                technical_score
            ),
            reason=(
                "Contribuição do Score Técnico "
                "para o Score Integrado."
            ),
            value=technical_score,
            weight=technical_weight * 100,
        ),

        "fundamental_score": create_breakdown_item(
            points=(
                fundamental_score
                * fundamental_weight
            ),
            signal=get_signal_from_score(
                fundamental_score
            ),
            reason=(
                "Contribuição do Score Fundamentalista "
                "para o Score Integrado."
            ),
            value=fundamental_score,
            weight=fundamental_weight * 100,
        ),

        "score": {
            "points": integrated_score,
            "signal": signal,
            "reason": (
                "Resultado consolidado entre "
                "análise técnica e fundamentalista."
            ),
        },
    }

    return {
        "score": integrated_score,
        "classification": classification,
        "signal": signal,
        "technical_weight": technical_weight,
        "fundamental_weight": fundamental_weight,
        "breakdown": breakdown,
    }


# ==========================================================
# FUNÇÃO CONSOLIDADA
# ==========================================================

def calculate_investia_scores(
    indicators,
    fundamentals,
    technical_weight=0.50,
    fundamental_weight=0.50,
):
    """
    Calcula os três Scores do InvestIA PRO.

    Retorno:

    {
        "technical_score": ...,
        "fundamental_score": ...,
        "integrated_score": ...,
        "technical_breakdown": ...,
        "fundamental_breakdown": ...,
        "integrated_breakdown": ...
    }
    """

    technical_result = calculate_technical_score(
        indicators
    )

    fundamental_result = calculate_fundamental_score(
        fundamentals
    )

    integrated_result = calculate_integrated_score(
        technical_score=technical_result.get(
            "score",
            50,
        ),
        fundamental_score=fundamental_result.get(
            "score",
            50,
        ),
        technical_weight=technical_weight,
        fundamental_weight=fundamental_weight,
    )

    return {

        # ----------------------------------------------
        # TÉCNICO
        # ----------------------------------------------

        "technical_score": technical_result.get(
            "score",
            0,
        ),

        "technical_classification": technical_result.get(
            "classification",
            "NEUTRO",
        ),

        "technical_signal": technical_result.get(
            "signal",
            "NEUTRO",
        ),

        "technical_breakdown": technical_result.get(
            "breakdown",
            {},
        ),

        # ----------------------------------------------
        # FUNDAMENTALISTA
        # ----------------------------------------------

        "fundamental_score": fundamental_result.get(
            "score",
            50,
        ),

        "fundamental_classification": fundamental_result.get(
            "classification",
            "NEUTRO",
        ),

        "fundamental_signal": fundamental_result.get(
            "signal",
            "NEUTRO",
        ),

        "fundamental_breakdown": fundamental_result.get(
            "breakdown",
            {},
        ),

        # ----------------------------------------------
        # INTEGRADO
        # ----------------------------------------------

        "integrated_score": integrated_result.get(
            "score",
            50,
        ),

        "integrated_classification": integrated_result.get(
            "classification",
            "NEUTRO",
        ),

        "integrated_signal": integrated_result.get(
            "signal",
            "NEUTRO",
        ),

        "integrated_breakdown": integrated_result.get(
            "breakdown",
            {},
        ),

        # ----------------------------------------------
        # PESOS
        # ----------------------------------------------

        "technical_weight": integrated_result.get(
            "technical_weight",
            0.50,
        ),

        "fundamental_weight": integrated_result.get(
            "fundamental_weight",
            0.50,
        ),
    }


# ==========================================================
# COMPATIBILIDADE COM VERSÕES ANTERIORES
# ==========================================================

def calculate_investia_score(
    data,
    asset=None,
):
    """
    Função de compatibilidade.

    Permite que módulos antigos que ainda utilizam
    calculate_investia_score() continuem funcionando.

    Aceita:
    - dados técnicos diretamente
    - dicionário contendo indicators
    - dicionário contendo fundamentals
    """

    if not isinstance(data, dict):
        data = {}

    indicators = data.get(
        "indicators",
        data,
    )

    fundamentals = data.get(
        "fundamentals",
        {},
    )

    result = calculate_investia_scores(
        indicators=indicators,
        fundamentals=fundamentals,
    )

    return result


# ==========================================================
# TESTE LOCAL
# ==========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("InvestIA PRO - Score.py")
    print("Fase 3.0.7")
    print("=" * 60)

    test_indicators = {

        "short_trend": "ALTA",

        "long_trend": "ALTA",

        "distance_ma21": 0.03,

        "distance_ma200": 0.12,

        "rsi": 58,

        "relative_volume": 1.20,

        "range_position": 0.70,

        "annual_volatility": 0.32,
    }

    test_fundamentals = {

        "trailingPE": 8.5,

        "priceToBook": 1.2,

        "returnOnEquity": 0.18,

        "profitMargins": 0.15,

        "debtToEbitda": 1.8,

        "revenueGrowth": 0.12,

        "dividendYield": 0.06,
    }

    result = calculate_investia_scores(
        indicators=test_indicators,
        fundamentals=test_fundamentals,
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

    print(
        "SINAL:",
        result["integrated_signal"],
    )
