"""
InvestIA PRO - Módulo de Análise Qualitativa e Resumo Executivo
"""
from indicators import compute_technical_indicators
from score import calculate_investia_score

def analyze_asset(market_data: dict) -> dict:
    """
    Processa dados do mercado, calcula indicadores e score,
    e gera parecer executivo detalhado.
    """
    if not market_data.get("is_valid"):
        return {
            "is_valid": False,
            "error": market_data.get("error", "Dados de mercado inválidos.")
        }

    indicators = compute_technical_indicators(market_data)
    score_info = calculate_investia_score(indicators, market_data.get("change_percent", 0.0))

    rsi = indicators["rsi"]
    rsi_status = "Neutro"
    if rsi > 70:
        rsi_status = "Sobrecomprado"
    elif rsi > 60:
        rsi_status = "Aquecido"
    elif rsi < 30:
        rsi_status = "Sobrevendido"
    elif rsi < 40:
        rsi_status = "Descontado"

    volatility = indicators["volatility"]
    risk = "Baixo" if volatility < 20 else ("Moderado" if volatility <= 35 else "Elevado")

    trend = "Alta" if indicators["price_above_ma21"] and indicators["price_above_ma200"] else (
        "Neutra / Mista" if indicators["price_above_ma21"] or indicators["price_above_ma200"] else "Baixa"
    )

    reasons = []
    if indicators["price_above_ma21"]:
        reasons.append("Preço acima da média móvel de curto prazo (MA21).")
    else:
        reasons.append("Preço abaixo da MA21 indica pressão vendedora no curto prazo.")

    if indicators["price_above_ma200"]:
        reasons.append("Tendência principal de longo prazo positiva (acima da MA200).")
    else:
        reasons.append("Operando abaixo da MA200 - atenção ao risco de estrutura.")

    if 40 <= rsi <= 60:
        reasons.append("RSI em zona de equilíbrio ideal para continuidade.")
    elif rsi > 70:
        reasons.append("RSI acima de 70 indica estiramento dos preços (sobrecompra).")
    elif rsi < 30:
        reasons.append("RSI abaixo de 30 indica oportunidade potencial de repique.")

    recommendation = (
        f"O ativo {market_data['asset']} apresenta cenário favorável com Score {score_info['score_total']}/100."
        if score_info['signal'] == "COMPRA" else
        f"Recomenda-se cautela para {market_data['asset']}. Manter em observação (Score {score_info['score_total']}/100)."
    )

    executive_summary = (
        f"Ativo {market_data['asset']} negociado a R$ {market_data['price']:.2f}. "
        f"Tendência geral é de {trend.lower()} com risco {risk.lower()} (volatilidade em {volatility:.1f}%). "
        f"Sinal gerado: {score_info['signal_icon']} {score_info['signal']} ({score_info['classification']})."
    )

    return {
        "is_valid": True,
        "asset": market_data["asset"],
        "price": market_data["price"],
        "change_percent": market_data["change_percent"],
        "score": score_info["score_total"],
        "classification": score_info["classification"],
        "signal": score_info["signal"],
        "signal_level": score_info["signal_level"],
        "signal_icon": score_info["signal_icon"],
        "trend": trend,
        "risk": risk,
        "rsi": rsi,
        "rsi_status": rsi_status,
        "volatility": volatility,
        "ma21": indicators["ma21"],
        "ma200": indicators["ma200"],
        "recommendation": recommendation,
        "reasons": reasons,
        "breakdown": score_info["breakdown"],
        "executive_summary": executive_summary,
        "history": market_data["history"]
    }
