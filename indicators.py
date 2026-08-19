"""
InvestIA PRO
Indicadores Técnicos

Versão: v0.6
Fase: 2.9.7 - Indicadores Robustos
"""

import math

import pandas as pd


# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

MA21_PERIOD = 21
MA200_PERIOD = 200

RSI_PERIOD = 14

VOLATILITY_PERIOD = 21


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

        result = float(value)

        if math.isnan(result):
            return None

        if math.isinf(result):
            return None

        return result

    except (
        TypeError,
        ValueError,
    ):

        return None


def get_history(market):
    """
    Obtém o histórico do ativo de maneira segura.

    Compatível com a estrutura produzida
    pelo market.py da Fase 2.9.7.
    """

    if market is None:
        return None

    if isinstance(
        market,
        pd.DataFrame,
    ):

        history = market

    elif isinstance(
        market,
        dict,
    ):

        history = market.get(
            "history"
        )

    else:

        return None

    if history is None:
        return None

    if not isinstance(
        history,
        pd.DataFrame,
    ):

        return None

    if history.empty:
        return None

    return history.copy()


def normalize_columns(history):
    """
    Normaliza as colunas do histórico.
    """

    if history is None:
        return None

    data = history.copy()

    # ------------------------------------------------------
    # MultiIndex
    # ------------------------------------------------------

    if isinstance(
        data.columns,
        pd.MultiIndex,
    ):

        new_columns = []

        for column in data.columns:

            if isinstance(
                column,
                tuple,
            ):

                new_columns.append(
                    str(
                        column[0]
                    )
                )

            else:

                new_columns.append(
                    str(column)
                )

        data.columns = new_columns

    # ------------------------------------------------------
    # Padronização
    # ------------------------------------------------------

    rename_map = {}

    for column in data.columns:

        column_str = str(
            column
        ).strip()

        lower = column_str.lower()

        if lower == "close":
            rename_map[column] = "Close"

        elif lower == "adj close":
            rename_map[column] = "Adj Close"

        elif lower == "open":
            rename_map[column] = "Open"

        elif lower == "high":
            rename_map[column] = "High"

        elif lower == "low":
            rename_map[column] = "Low"

        elif lower == "volume":
            rename_map[column] = "Volume"

    if rename_map:

        data = data.rename(
            columns=rename_map
        )

    return data


def get_close_series(history):
    """
    Retorna a série de fechamento.
    """

    if history is None:
        return None

    if "Close" not in history.columns:

        return None

    close = history[
        "Close"
    ].copy()

    close = pd.to_numeric(
        close,
        errors="coerce",
    )

    close = close.dropna()

    if close.empty:

        return None

    return close


# ==========================================================
# MÉDIA MÓVEL
# ==========================================================

def calculate_ma(
    close,
    period,
):
    """
    Calcula uma média móvel simples.
    """

    if close is None:

        return None

    try:

        if len(close) < period:

            return None

        ma = (
            close
            .rolling(
                window=period,
                min_periods=period,
            )
            .mean()
        )

        if ma.empty:

            return None

        return safe_float(
            ma.iloc[-1]
        )

    except Exception:

        return None


# ==========================================================
# RSI
# ==========================================================

def calculate_rsi(
    close,
    period=RSI_PERIOD,
):
    """
    Calcula o RSI utilizando o método
    clássico baseado em ganhos e perdas.
    """

    if close is None:

        return None

    try:

        if len(close) < period + 1:

            return None

        delta = close.diff()

        gain = delta.clip(
            lower=0
        )

        loss = -delta.clip(
            upper=0
        )

        avg_gain = (
            gain
            .rolling(
                window=period,
                min_periods=period,
            )
            .mean()
        )

        avg_loss = (
            loss
            .rolling(
                window=period,
                min_periods=period,
            )
            .mean()
        )

        latest_gain = safe_float(
            avg_gain.iloc[-1]
        )

        latest_loss = safe_float(
            avg_loss.iloc[-1]
        )

        if latest_gain is None:

            return None

        if latest_loss is None:

            return None

        # --------------------------------------------------
        # Caso não existam perdas
        # --------------------------------------------------

        if latest_loss == 0:

            if latest_gain > 0:

                return 100.0

            return 50.0

        rs = (
            latest_gain
            / latest_loss
        )

        rsi = (
            100
            - (
                100
                / (
                    1
                    + rs
                )
            )
        )

        return safe_float(
            rsi
        )

    except Exception:

        return None


# ==========================================================
# RETORNOS
# ==========================================================

def calculate_returns(
    close,
):
    """
    Calcula retornos percentuais diários.
    """

    if close is None:

        return None

    try:

        returns = (
            close
            .pct_change()
            .dropna()
        )

        if returns.empty:

            return None

        return returns

    except Exception:

        return None


# ==========================================================
# VOLATILIDADE
# ==========================================================

def calculate_volatility(
    close,
    period=VOLATILITY_PERIOD,
):
    """
    Calcula a volatilidade histórica diária
    utilizando o desvio-padrão dos retornos.
    """

    returns = calculate_returns(
        close
    )

    if returns is None:

        return None

    try:

        if len(returns) < period:

            return None

        volatility = (
            returns
            .rolling(
                window=period,
                min_periods=period,
            )
            .std()
        )

        value = safe_float(
            volatility.iloc[-1]
        )

        return value

    except Exception:

        return None


# ==========================================================
# VARIAÇÃO DIÁRIA
# ==========================================================

def calculate_daily_change(
    close,
):
    """
    Calcula a variação percentual do
    último fechamento em relação ao anterior.
    """

    if close is None:

        return None

    try:

        if len(close) < 2:

            return None

        previous = safe_float(
            close.iloc[-2]
        )

        current = safe_float(
            close.iloc[-1]
        )

        if previous is None:
            return None

        if current is None:
            return None

        if previous == 0:

            return None

        change = (
            (
                current
                - previous
            )
            / previous
        )

        return safe_float(
            change
        )

    except Exception:

        return None


# ==========================================================
# TENDÊNCIA
# ==========================================================

def determine_trend(
    price,
    ma21,
    ma200,
):
    """
    Determina a tendência básica utilizando
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

    if price is None:

        return "Indisponível"

    if ma21 is None:

        return "Indisponível"

    if ma200 is None:

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
# CÁLCULO PRINCIPAL
# ==========================================================

def calculate_indicators(
    market,
):
    """
    Calcula todos os indicadores utilizados
    pelo InvestIA PRO.

    Estrutura esperada:

    {
        "asset": "...",
        "ticker": "...",
        "history": DataFrame,
        "price": ...
    }

    Retorna:

    {
        "asset": "...",
        "ticker": "...",
        "price": ...,
        "ma21": ...,
        "ma200": ...,
        "rsi": ...,
        "volatility": ...,
        "daily_change": ...,
        "trend": "..."
    }
    """

    if market is None:

        return None

    # ======================================================
    # HISTÓRICO
    # ======================================================

    history = get_history(
        market
    )

    if history is None:

        return None

    history = normalize_columns(
        history
    )

    if history is None:

        return None

    # ======================================================
    # CLOSE
    # ======================================================

    close = get_close_series(
        history
    )

    if close is None:

        return None

    # ======================================================
    # ASSET
    # ======================================================

    asset = None
    ticker = None
    market_price = None

    if isinstance(
        market,
        dict,
    ):

        asset = market.get(
            "asset"
        )

        ticker = market.get(
            "ticker"
        )

        market_price = market.get(
            "price"
        )

    # ======================================================
    # PREÇO
    # ======================================================

    price = safe_float(
        market_price
    )

    if price is None:

        try:

            price = safe_float(
                close.iloc[-1]
            )

        except Exception:

            price = None

    if price is None:

        return None

    # ======================================================
    # MA21
    # ======================================================

    ma21 = calculate_ma(
        close,
        MA21_PERIOD,
    )

    # ======================================================
    # MA200
    # ======================================================

    ma200 = calculate_ma(
        close,
        MA200_PERIOD,
    )

    # ======================================================
    # RSI
    # ======================================================

    rsi = calculate_rsi(
        close,
        RSI_PERIOD,
    )

    # ======================================================
    # VOLATILIDADE
    # ======================================================

    volatility = calculate_volatility(
        close,
        VOLATILITY_PERIOD,
    )

    # ======================================================
    # VARIAÇÃO DIÁRIA
    # ======================================================

    daily_change = calculate_daily_change(
        close
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
    # RETORNO
    # ======================================================

    return {

        "asset":
            asset,

        "ticker":
            ticker,

        "price":
            price,

        "ma21":
            ma21,

        "ma200":
            ma200,

        "rsi":
            rsi,

        "volatility":
            volatility,

        "daily_change":
            daily_change,

        "trend":
            trend,
    }


# ==========================================================
# VALIDAÇÃO DOS INDICADORES
# ==========================================================

def validate_indicators(
    indicators,
):
    """
    Verifica se os principais indicadores
    estão disponíveis.
    """

    if indicators is None:

        return False

    if not isinstance(
        indicators,
        dict,
    ):

        return False

    required = [
        "price",
        "ma21",
        "ma200",
        "rsi",
        "volatility",
    ]

    for field in required:

        value = indicators.get(
            field
        )

        if value is None:

            return False

    return True


# ==========================================================
# RESUMO
# ==========================================================

def get_indicator_summary(
    indicators,
):
    """
    Retorna um resumo simples dos indicadores.
    """

    if indicators is None:

        return {}

    if not isinstance(
        indicators,
        dict,
    ):

        return {}

    return {

        "price":
            indicators.get(
                "price"
            ),

        "ma21":
            indicators.get(
                "ma21"
            ),

        "ma200":
            indicators.get(
                "ma200"
            ),

        "rsi":
            indicators.get(
                "rsi"
            ),

        "volatility":
            indicators.get(
                "volatility"
            ),

        "daily_change":
            indicators.get(
                "daily_change"
            ),

        "trend":
            indicators.get(
                "trend"
            ),
    }
