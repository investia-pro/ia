"""
InvestIA PRO - Módulo do Score InvestIA e Métricas de Decisão
"""
from config import SCORE_WEIGHTS

def calculate_investia_score(indicators: dict, change_percent: float = 0.0) -> dict:
    """
    Transforma indicadores técnicos em uma pontuação objetiva de 0 a 100.
    """
    price_above_ma21 = indicators.get("price_above_ma21", False)
    price_above_ma200 = indicators.get("price_above_ma200", False)
    rsi = indicators.get("rsi", 50.0)
    volatility = indicators.get("volatility", 0.0)

    # 1. Componente Tendência (peso 40)
    trend_points = 0.0
    if price_above_ma21 and price_above_ma200:
        trend_points = 40.0
    elif price_above_ma21:
        trend_points = 25.0
    elif price_above_ma200:
        trend_points = 20.0
    else:
        trend_points = 5.0

    # 2. Componente RSI (peso 35)
    rsi_points = 0.0
    if 40 <= rsi <= 60:
        rsi_points = 35.0  # Zona ideal de impulso sem sobrecompra
    elif 30 <= rsi < 40:
        rsi_points = 28.0  # Zona de oportunidade / sobrevenda
    elif 60 < rsi <= 70:
        rsi_points = 25.0  # Tendência forte, mas aproximando do topo
    elif rsi > 70:
        rsi_points = 10.0  # Sobrecomprado (risco de correção)
    else:  # rsi < 30
        rsi_points = 15.0  # Altamente sobrevendido

    # 3. Componente Volatilidade & Risco (peso 25)
    vol_points = 0.0
    if volatility < 20.0:
        vol_points = 25.0
    elif 20.0 <= volatility <= 35.0:
        vol_points = 20.0
    elif 35.0 < volatility <= 50.0:
        vol_points = 12.0
    else:
        vol_points = 5.0

    total_score = min(100.0, max(0.0, trend_points + rsi_points + vol_points))

    # Classificação e Sinais
    if total_score >= 80:
        classification = "Forte Compra"
        signal = "COMPRA"
        signal_level = "Alta"
        signal_icon = "🚀"
    elif total_score >= 65:
        classification = "Compra"
        signal = "COMPRA"
        signal_level = "Moderada"
        signal_icon = "✅"
    elif total_score >= 45:
        classification = "Neutro / Manter"
        signal = "NEUTRO"
        signal_level = "Neutro"
        signal_icon = "⏸️"
    elif total_score >= 30:
        classification = "Atenção / Venda"
        signal = "VENDA"
        signal_level = "Moderada"
        signal_icon = "⚠️"
    else:
        classification = "Forte Venda"
        signal = "VENDA"
        signal_level = "Alta"
        signal_icon = "🔴"

    return {
        "score_total": round(total_score, 1),
        "classification": classification,
        "signal": signal,
        "signal_level": signal_level,
        "signal_icon": signal_icon,
        "breakdown": {
            "trend_score": trend_points,
            "rsi_score": rsi_points,
            "volatility_score": vol_points
        }
    }
