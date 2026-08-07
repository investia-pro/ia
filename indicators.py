"""
InvestIA PRO
Indicadores Técnicos

Versão: v0.5.3 Stable
"""

import numpy as np

from config import (
    RSI_PERIOD,
    SHORT_MA,
    LONG_MA,
    VOLATILITY_WINDOW,
)


def calculate_indicators(market):

    history = market["history"]

    close = history["Close"]

    # =====================
    # Médias móveis
    # =====================

    ma21 = close.rolling(
        SHORT_MA
    ).mean().iloc[-1]

    ma200 = close.rolling(
        LONG_MA
    ).mean().iloc[-1]

    # =====================
    # RSI
    # =====================

    delta = close.diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(
        RSI_PERIOD
    ).mean()

    avg_loss = loss.rolling(
        RSI_PERIOD
    ).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    rsi = 100 - (100 / (1 + rs))

    # =====================
    # Volatilidade
    # =====================

    volatility = (
        close
        .pct_change()
        .rolling(VOLATILITY_WINDOW)
        .std()
        .iloc[-1]
    )

    return {

        "asset": market["asset"],

        "price": market["price"],

        "history": history,

        "ma21": float(ma21),

        "ma200": float(ma200),

        "rsi": float(rsi.iloc[-1]),

        "volatility": float(volatility)

    }
