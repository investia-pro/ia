"""
InvestIA PRO
Indicadores Técnicos

Versão: v0.7
Fase: 3.0.5 - Histórico e Evolução dos Indicadores

Responsabilidades:
- Calcular MA21
- Calcular MA200
- Calcular RSI
- Calcular volatilidade
- Preparar indicadores históricos
- Manter compatibilidade com o motor atual
"""

import pandas as pd


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def safe_float(
    value,
    default=None,
):
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

    if pd.isna(value):

        return default

    return value


def get_market_history(
    market,
):
    """
    Obtém o histórico do mercado com segurança.

    Aceita:
    - Dicionário preparado pelo market.py
    - DataFrame diretamente
    """

    if isinstance(
        market,
        pd.DataFrame,
    ):

        return market.copy()

    if isinstance(
        market,
        dict,
    ):

        history = market.get(
            "history"
        )

        if isinstance(
            history,
            pd.DataFrame,
        ):

            return history.copy()

    return None


def get_close_column(
    history,
):
    """
    Localiza a coluna de fechamento.
    """

    if not isinstance(
        history,
        pd.DataFrame,
    ):

        return None

    possible_columns = [

        "Close",
        "close",
        "Adj Close",
        "adj_close",

    ]

    for column in possible_columns:

        if column in history.columns:

            return column

    return None


def normalize_history(
    history,
):
    """
    Normaliza o histórico para cálculo
    dos indicadores.
    """

    if not isinstance(
        history,
        pd.DataFrame,
    ):

        return None

    if history.empty:

        return None

    history = history.copy()

    close_column = get_close_column(
        history
    )

    if close_column is None:

        return None

    history[close_column] = pd.to_numeric(
        history[close_column],
        errors="coerce",
    )

    history = history.dropna(
        subset=[
            close_column
        ]
    )

    if history.empty:

        return None

    return history


# ==========================================================
# MÉDIA MÓVEL
# ==========================================================

def calculate_moving_average(
    series,
    window,
):
    """
    Calcula uma média móvel simples.
    """

    if not isinstance(
        series,
        pd.Series,
    ):

        return None

    if series.empty:

        return None

    if len(series) < window:

        return None

    value = (
        series
        .rolling(
            window=window,
            min_periods=window,
        )
        .mean()
        .iloc[-1]
    )

    return safe_float(
        value
    )


# ==========================================================
# RSI
# ==========================================================

def calculate_rsi_series(
    close,
    period=14,
):
    """
    Calcula a série histórica do RSI.

    Utiliza médias móveis exponenciais
    para suavização dos ganhos e perdas.
    """

    if not isinstance(
        close,
        pd.Series,
    ):

        return None

    if len(close) < period + 1:

        return None

    delta = close.diff()

    gains = delta.clip(
        lower=0
    )

    losses = (
        -delta.clip(
            upper=0
        )
    )

    average_gain = gains.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period,
    ).mean()

    average_loss = losses.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period,
    ).mean()

    average_loss = average_loss.replace(
        0,
        pd.NA,
    )

    rs = (
        average_gain
        / average_loss
    )

    rsi = (
        100
        - (
            100
            / (
                1 + rs
            )
        )
    )

    return rsi


def calculate_rsi(
    series,
    period=14,
):
    """
    Retorna o valor mais recente do RSI.
    """

    rsi_series = calculate_rsi_series(
        series,
        period,
    )

    if rsi_series is None:

        return None

    valid_rsi = rsi_series.dropna()

    if valid_rsi.empty:

        return None

    return safe_float(
        valid_rsi.iloc[-1]
    )


# ==========================================================
# VOLATILIDADE
# ==========================================================

def calculate_volatility(
    close,
    window=21,
):
    """
    Calcula a volatilidade baseada no
    desvio padrão dos retornos diários.
    """

    if not isinstance(
        close,
        pd.Series,
    ):

        return None

    if len(close) < window + 1:

        return None

    returns = close.pct_change()

    volatility = (
        returns
        .rolling(
            window=window,
            min_periods=window,
        )
        .std()
        .iloc[-1]
    )

    return safe_float(
        volatility
    )


# ==========================================================
# DATAFRAME DE INDICADORES HISTÓRICOS
# ==========================================================

def calculate_historical_indicators(
    market,
    ma21_window=21,
    ma200_window=200,
    rsi_period=14,
    volatility_window=21,
):
    """
    Calcula indicadores técnicos para todo
    o histórico disponível.

    Retorna um DataFrame contendo:

    - price
    - ma21
    - ma200
    - rsi
    - volatility

    Cada linha representa um ponto no tempo
    que poderá ser utilizado para calcular
    o Score Técnico histórico.
    """

    history = get_market_history(
        market
    )

    history = normalize_history(
        history
    )

    if history is None:

        return pd.DataFrame()

    close_column = get_close_column(
        history
    )

    if close_column is None:

        return pd.DataFrame()

    close = (
        pd.to_numeric(
            history[close_column],
            errors="coerce",
        )
        .dropna()
    )

    if close.empty:

        return pd.DataFrame()

    # ======================================================
    # DATAFRAME BASE
    # ======================================================

    indicators = pd.DataFrame(
        index=close.index
    )

    indicators["price"] = close

    # ======================================================
    # MA21
    # ======================================================

    indicators["ma21"] = (
        close
        .rolling(
            window=ma21_window,
            min_periods=ma21_window,
        )
        .mean()
    )

    # ======================================================
    # MA200
    # ======================================================

    indicators["ma200"] = (
        close
        .rolling(
            window=ma200_window,
            min_periods=ma200_window,
        )
        .mean()
    )

    # ======================================================
    # RSI
    # ======================================================

    indicators["rsi"] = calculate_rsi_series(
        close,
        period=rsi_period,
    )

    # ======================================================
    # VOLATILIDADE
    # ======================================================

    returns = close.pct_change()

    indicators["volatility"] = (
        returns
        .rolling(
            window=volatility_window,
            min_periods=volatility_window,
        )
        .std()
    )

    # ======================================================
    # LIMPEZA
    # ======================================================

    indicators = indicators.replace(
        [
            float("inf"),
            float("-inf"),
        ],
        pd.NA,
    )

    return indicators


# ==========================================================
# ÚLTIMOS INDICADORES
# ==========================================================

def get_latest_historical_indicators(
    historical_indicators,
):
    """
    Obtém o último conjunto válido de
    indicadores históricos.
    """

    if not isinstance(
        historical_indicators,
        pd.DataFrame,
    ):

        return {}

    if historical_indicators.empty:

        return {}

    required_columns = [

        "price",
        "ma21",
        "ma200",
        "rsi",

    ]

    valid_data = (
        historical_indicators
        .dropna(
            subset=required_columns
        )
    )

    if valid_data.empty:

        return {}

    latest = valid_data.iloc[-1]

    return {

        "price":
            safe_float(
                latest.get(
                    "price"
                )
            ),

        "ma21":
            safe_float(
                latest.get(
                    "ma21"
                )
            ),

        "ma200":
            safe_float(
                latest.get(
                    "ma200"
                )
            ),

        "rsi":
            safe_float(
                latest.get(
                    "rsi"
                )
            ),

        "volatility":
            safe_float(
                latest.get(
                    "volatility"
                )
            ),
    }


# ==========================================================
# INDICADORES ATUAIS
# ==========================================================

def calculate_indicators(
    market,
):
    """
    Calcula os indicadores técnicos atuais.

    Mantém compatibilidade com as fases
    anteriores do InvestIA PRO.

    Retorno:

    {
        "asset": ...,
        "price": ...,
        "ma21": ...,
        "ma200": ...,
        "rsi": ...,
        "volatility": ...,
        "historical": DataFrame
    }
    """

    if market is None:

        raise ValueError(
            "Dados de mercado não fornecidos."
        )

    # ======================================================
    # HISTÓRICO DE INDICADORES
    # ======================================================

    historical = calculate_historical_indicators(
        market
    )

    if historical.empty:

        raise ValueError(
            "Não foi possível calcular "
            "os indicadores históricos."
        )

    # ======================================================
    # ÚLTIMO CONJUNTO VÁLIDO
    # ======================================================

    latest = get_latest_historical_indicators(
        historical
    )

    if not latest:

        raise ValueError(
            "Não existem dados suficientes "
            "para calcular os indicadores."
        )

    # ======================================================
    # ATIVO
    # ======================================================

    asset = None

    if isinstance(
        market,
        dict,
    ):

        asset = market.get(
            "asset"
        )

        if asset is None:

            asset = market.get(
                "ticker"
            )

    # ======================================================
    # PREÇO
    # ======================================================

    market_price = None

    if isinstance(
        market,
        dict,
    ):

        market_price = safe_float(
            market.get(
                "price"
            )
        )

    price = (
        market_price
        if market_price is not None
        else latest["price"]
    )

    # ======================================================
    # RETORNO
    # ======================================================

    return {

        "asset":
            asset,

        "price":
            price,

        "ma21":
            latest["ma21"],

        "ma200":
            latest["ma200"],

        "rsi":
            latest["rsi"],

        "volatility":
            latest["volatility"],

        "historical":
            historical,
    }


# ==========================================================
# FUNÇÃO DE COMPATIBILIDADE
# ==========================================================

def get_historical_indicators(
    market,
):
    """
    Alias para obtenção dos indicadores
    históricos.

    Utilizado pelas próximas fases para
    facilitar a integração.
    """

    return calculate_historical_indicators(
        market
    )
