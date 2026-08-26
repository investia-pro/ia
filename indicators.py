"""
InvestIA PRO - Módulo de Cálculo de Indicadores Técnicos
"""
import pandas as pd
import numpy as np

def calculate_rsi(series: pd.Series, period: int = 14) -> float:
    """Calcula o RSI (Índice de Força Relativa) usando média móvel exponencial."""
    if len(series) < period + 1:
        return 50.0

    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/period, adjust=False).mean()

    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    last_rsi = rsi.iloc[-1]
    
    if pd.isna(last_rsi):
        return 50.0
    return float(np.clip(last_rsi, 0, 100))

def compute_technical_indicators(market_data: dict) -> dict:
    """
    Recebe o dicionário padronizado do market.py e anexa os indicadores.
    """
    history = market_data.get("history")
    
    indicators = {
        "ma21": None,
        "ma200": None,
        "rsi": 50.0,
        "volatility": 0.0,
        "trend_ma21": "Neutro",
        "trend_ma200": "Neutro",
        "price_above_ma21": False,
        "price_above_ma200": False
    }

    if history is None or history.empty or len(history) < 5:
        return indicators

    close_series = history["Close"]
    current_price = market_data.get("price") or close_series.iloc[-1]

    # Médias Móveis
    ma21_val = float(close_series.rolling(window=21, min_periods=1).mean().iloc[-1])
    ma200_val = float(close_series.rolling(window=200, min_periods=1).mean().iloc[-1])

    # Volatilidade (Desvio Padrão percentual anualizado dos retornos diários)
    daily_returns = close_series.pct_change().dropna()
    volatility_val = float(daily_returns.std() * np.sqrt(252) * 100) if len(daily_returns) > 5 else 0.0

    # RSI
    rsi_val = calculate_rsi(close_series, period=14)

    indicators["ma21"] = round(ma21_val, 2)
    indicators["ma200"] = round(ma200_val, 2)
    indicators["rsi"] = round(rsi_val, 2)
    indicators["volatility"] = round(volatility_val, 2)
    indicators["price_above_ma21"] = current_price > ma21_val
    indicators["price_above_ma200"] = current_price > ma200_val
    indicators["trend_ma21"] = "Alta" if current_price > ma21_val else "Baixa"
    indicators["trend_ma200"] = "Alta" if current_price > ma200_val else "Baixa"

    return indicators
