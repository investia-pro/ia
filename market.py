"""
InvestIA PRO
Camada de Dados de Mercado

Versão: v0.5.3 Stable
"""

import yfinance as yf
import streamlit as st

from config import (
    CACHE_TTL,
    MARKET_SUFFIX,
    DEFAULT_PERIOD,
)

from utils import (
    validate_market_data,
)


@st.cache_data(ttl=CACHE_TTL)
def get_market_data(asset: str, period: str = DEFAULT_PERIOD):
    """
    Busca dados históricos de um ativo.

    Retorna:
    {
        asset,
        price,
        history
    }
    """

    asset = asset.strip().upper()

    if not asset:
        return None

    ticker = yf.Ticker(f"{asset}{MARKET_SUFFIX}")

    try:

        history = ticker.history(
            period=period,
            auto_adjust=True
        )

    except Exception:
        return None

    if not validate_market_data(history):
        return None

    return {

        "asset": asset,

        "price": float(history["Close"].iloc[-1]),

        "history": history

    }
