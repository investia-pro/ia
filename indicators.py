"""
InvestIA PRO
Módulo de Indicadores Técnicos

Versão: v3.1.3
Fase Final: 3.1.3

Responsabilidades:
- Médias móveis
- RSI
- Volatilidade
- Distâncias das médias
- Tendência
- Range do período
- Volume relativo
- Métricas de performance

Compatível com:
- market.py Fase 3.0.7
- analysis.py Fase 3.0.6+
- score.py Fase 3.0.6+
- app.py Fase 3.0.6+
"""

import math
import pandas as pd
import numpy as np


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

    if pd.isna(value):
        return default

    try:
        if not math.isfinite(value):
            return default
    except (TypeError, ValueError):
        return default

    return value


def get_history(prepared_data):
    """
    Obtém o histórico com segurança.
    """

    if not isinstance(prepared_data, dict):
        return pd.DataFrame()

    history = prepared_data.get("history")

    if history is None:
        return pd.DataFrame()

    if not isinstance(history, pd.DataFrame):
        try:
            history = pd.DataFrame(history)
        except Exception:
            return pd.DataFrame()

    if history.empty:
        return pd.DataFrame()

    return history.copy()


def get_price_column(history):
    """
    Localiza a coluna mais apropriada para análise de preço.
    """

    if not isinstance(history, pd.DataFrame):
        return None

    if history.empty:
        return None

    preferred_columns = [
        "Close",
        "Adj Close",
        "close",
        "adj_close",
    ]

    for column in preferred_columns:
        if column in history.columns:
            return column

    return None


def get_volume_column(history):
    """
    Localiza a coluna de volume.
    """

    if not isinstance(history, pd.DataFrame):
        return None

    possible_columns = [
        "Volume",
        "volume",
    ]

    for column in possible_columns:
        if column in history.columns:
            return column

    return None


def get_numeric_series(history, column):
    """
    Retorna uma série numérica limpa.
    """

    if (
        not isinstance(history, pd.DataFrame)
        or column not in history.columns
    ):
        return pd.Series(dtype=float)

    try:
        series = pd.to_numeric(
            history[column],
            errors="coerce",
        )

        return series.dropna()

    except Exception:
        return pd.Series(dtype=float)


def calculate_distance(current_price, reference_price):
    """
    Calcula a distância percentual entre o preço atual
    e um valor de referência.

    Retorno decimal:
    0.05 = 5%
    -0.05 = -5%
    """

    current_price = safe_float(current_price)
    reference_price = safe_float(reference_price)

    if (
        current_price is None
        or reference_price is None
        or reference_price == 0
    ):
        return None

    return (
        current_price / reference_price
    ) - 1


# ==========================================================
# MÉDIAS MÓVEIS
# ==========================================================

def calculate_moving_average(
    prices,
    window,
):
    """
    Calcula a média móvel simples.
    """

    if prices is None:
        return None

    try:
        prices = pd.Series(prices).dropna()

        if len(prices) < window:
            return None

        value = prices.rolling(
            window=window
        ).mean().iloc[-1]

        return safe_float(value)

    except Exception:
        return None


# ==========================================================
# RSI
# ==========================================================

def calculate_rsi(
    prices,
    period=14,
):
    """
    Calcula o Relative Strength Index (RSI).

    Retorno entre 0 e 100.
    """

    if prices is None:
        return None

    try:
        prices = pd.Series(prices).dropna()

        if len(prices) < period + 1:
            return None

        delta = prices.diff()

        gain = delta.clip(
            lower=0
        )

        loss = -delta.clip(
            upper=0
        )

        average_gain = gain.ewm(
            alpha=1 / period,
            adjust=False,
            min_periods=period,
        ).mean()

        average_loss = loss.ewm(
            alpha=1 / period,
            adjust=False,
            min_periods=period,
        ).mean()

        last_gain = safe_float(
            average_gain.iloc[-1]
        )

        last_loss = safe_float(
            average_loss.iloc[-1]
        )

        if last_gain is None or last_loss is None:
            return None

        if last_loss == 0:

            if last_gain > 0:
                return 100.0

            return 50.0

        rs = last_gain / last_loss

        rsi = 100 - (
            100 / (1 + rs)
        )

        return safe_float(rsi)

    except Exception:
        return None


# ==========================================================
# VOLATILIDADE
# ==========================================================

def calculate_volatility(
    prices,
    annualize=False,
):
    """
    Calcula a volatilidade dos retornos diários.

    Por padrão retorna volatilidade diária.

    Exemplo:
    0.02 = 2%
    """

    if prices is None:
        return None

    try:
        prices = pd.Series(prices).dropna()

        if len(prices) < 2:
            return None

        returns = prices.pct_change().dropna()

        if returns.empty:
            return None

        volatility = returns.std()

        if annualize:
            volatility = volatility * np.sqrt(252)

        return safe_float(volatility)

    except Exception:
        return None


# ==========================================================
# TENDÊNCIA
# ==========================================================

def classify_trend(
    current_price,
    ma21,
    ma200,
):
    """
    Classifica a tendência utilizando preço,
    MA21 e MA200.
    """

    current_price = safe_float(current_price)
    ma21 = safe_float(ma21)
    ma200 = safe_float(ma200)

    if current_price is None:
        return "N/D"

    # Sem MA200 ainda
    if ma21 is None:
        return "N/D"

    if ma200 is None:

        if current_price > ma21:
            return "ALTA"

        if current_price < ma21:
            return "BAIXA"

        return "NEUTRA"

    # Forte alta
    if (
        current_price > ma21
        and ma21 > ma200
    ):
        return "FORTE ALTA"

    # Alta com estrutura positiva
    if (
        current_price > ma200
        and ma21 >= ma200
    ):
        return "ALTA"

    # Baixa
    if (
        current_price < ma21
        and ma21 < ma200
    ):
        return "FORTE BAIXA"

    if current_price < ma200:
        return "BAIXA"

    return "NEUTRA"


def classify_short_trend(
    current_price,
    ma21,
):
    """
    Classifica tendência de curto prazo.
    """

    current_price = safe_float(current_price)
    ma21 = safe_float(ma21)

    if (
        current_price is None
        or ma21 is None
    ):
        return "N/D"

    distance = calculate_distance(
        current_price,
        ma21,
    )

    if distance is None:
        return "N/D"

    if distance >= 0.05:
        return "FORTE ALTA"

    if distance > 0:
        return "ALTA"

    if distance <= -0.05:
        return "FORTE BAIXA"

    if distance < 0:
        return "BAIXA"

    return "NEUTRA"


def classify_long_trend(
    current_price,
    ma200,
):
    """
    Classifica tendência de longo prazo.
    """

    current_price = safe_float(current_price)
    ma200 = safe_float(ma200)

    if (
        current_price is None
        or ma200 is None
    ):
        return "N/D"

    distance = calculate_distance(
        current_price,
        ma200,
    )

    if distance is None:
        return "N/D"

    if distance >= 0.10:
        return "FORTE ALTA"

    if distance > 0:
        return "ALTA"

    if distance <= -0.10:
        return "FORTE BAIXA"

    if distance < 0:
        return "BAIXA"

    return "NEUTRA"


# ==========================================================
# RANGE DO PERÍODO
# ==========================================================

def calculate_range_position(
    current_price,
    period_low,
    period_high,
):
    """
    Calcula a posição do preço no range.

    Retorno:
    0 = mínima
    1 = máxima
    """

    current_price = safe_float(current_price)
    period_low = safe_float(period_low)
    period_high = safe_float(period_high)

    if (
        current_price is None
        or period_low is None
        or period_high is None
    ):
        return None

    range_size = (
        period_high - period_low
    )

    if range_size <= 0:
        return None

    position = (
        current_price - period_low
    ) / range_size

    return safe_float(position)


def classify_range_position(position):
    """
    Classifica a posição dentro do range.
    """

    position = safe_float(position)

    if position is None:
        return "N/D"

    if position >= 0.80:
        return "PRÓXIMO DA MÁXIMA"

    if position >= 0.60:
        return "FAIXA SUPERIOR"

    if position <= 0.20:
        return "PRÓXIMO DA MÍNIMA"

    if position <= 0.40:
        return "FAIXA INFERIOR"

    return "FAIXA INTERMEDIÁRIA"


# ==========================================================
# VOLUME
# ==========================================================

def calculate_relative_volume(
    volume,
    average_volume,
):
    """
    Calcula o volume relativo.

    Exemplo:
    1.50 = volume 50% acima da média
    0.50 = volume 50% abaixo da média
    """

    volume = safe_float(volume)
    average_volume = safe_float(
        average_volume
    )

    if (
        volume is None
        or average_volume is None
        or average_volume == 0
    ):
        return None

    return volume / average_volume


def classify_volume(
    relative_volume,
):
    """
    Classifica o volume relativo.
    """

    relative_volume = safe_float(
        relative_volume
    )

    if relative_volume is None:
        return "N/D"

    if relative_volume >= 1.50:
        return "MUITO ALTO"

    if relative_volume >= 1.15:
        return "ALTO"

    if relative_volume <= 0.50:
        return "MUITO BAIXO"

    if relative_volume < 0.85:
        return "BAIXO"

    return "NORMAL"


# ==========================================================
# CLASSIFICAÇÃO RSI
# ==========================================================

def classify_rsi(
    rsi,
):
    """
    Classifica o RSI.
    """

    rsi = safe_float(rsi)

    if rsi is None:
        return "N/D"

    if rsi >= 70:
        return "SOBRECOMPRADO"

    if rsi >= 60:
        return "FORTE"

    if rsi > 40:
        return "NEUTRO"

    if rsi > 30:
        return "FRACO"

    return "SOBREVENDIDO"


# ==========================================================
# FUNÇÃO PRINCIPAL
# ==========================================================

def calculate_indicators(
    prepared_data,
):
    """
    Calcula todos os indicadores técnicos.

    O retorno é sempre um dicionário.

    Esta função é compatível com o app.py atual,
    mantendo as chaves principais:

    - price
    - ma21
    - ma200
    - rsi
    - volatility
    """

    # Estrutura padrão para evitar KeyError
    indicators = {

        # Preço
        "price": None,
        "current_price": None,
        "previous_close": None,

        # Médias
        "ma21": None,
        "ma200": None,

        # Distâncias
        "distance_ma21": None,
        "distance_ma200": None,

        # RSI
        "rsi": None,
        "rsi_status": "N/D",

        # Volatilidade
        "volatility": None,
        "annual_volatility": None,

        # Tendências
        "trend": "N/D",
        "short_trend": "N/D",
        "long_trend": "N/D",

        # Range
        "range_position": None,
        "range_status": "N/D",

        # Volume
        "volume": None,
        "average_volume": None,
        "relative_volume": None,
        "volume_status": "N/D",

        # Performance
        "daily_change": None,
        "daily_change_percent": None,
        "period_change": None,
        "period_change_percent": None,

        # Máxima e mínima
        "period_high": None,
        "period_low": None,
        "distance_from_high": None,
        "distance_from_low": None,
    }

    if not isinstance(prepared_data, dict):
        return indicators

    history = get_history(prepared_data)

    if history.empty:
        return indicators

    price_column = get_price_column(history)

    if price_column is None:
        return indicators

    prices = get_numeric_series(
        history,
        price_column,
    )

    if prices.empty:
        return indicators

    # ======================================================
    # PREÇO
    # ======================================================

    current_price = safe_float(
        prices.iloc[-1]
    )

    indicators["price"] = current_price
    indicators["current_price"] = current_price

    if len(prices) >= 2:

        previous_close = safe_float(
            prices.iloc[-2]
        )

        indicators[
            "previous_close"
        ] = previous_close

    # ======================================================
    # MÉDIAS
    # ======================================================

    ma21 = calculate_moving_average(
        prices,
        21,
    )

    ma200 = calculate_moving_average(
        prices,
        200,
    )

    indicators["ma21"] = ma21
    indicators["ma200"] = ma200

    # ======================================================
    # DISTÂNCIAS DAS MÉDIAS
    # ======================================================

    indicators[
        "distance_ma21"
    ] = calculate_distance(
        current_price,
        ma21,
    )

    indicators[
        "distance_ma200"
    ] = calculate_distance(
        current_price,
        ma200,
    )

    # ======================================================
    # RSI
    # ======================================================

    rsi = calculate_rsi(
        prices,
        period=14,
    )

    indicators["rsi"] = rsi

    indicators[
        "rsi_status"
    ] = classify_rsi(
        rsi
    )

    # ======================================================
    # VOLATILIDADE
    # ======================================================

    indicators[
        "volatility"
    ] = calculate_volatility(
        prices,
        annualize=False,
    )

    indicators[
        "annual_volatility"
    ] = calculate_volatility(
        prices,
        annualize=True,
    )

    # ======================================================
    # TENDÊNCIA
    # ======================================================

    indicators[
        "trend"
    ] = classify_trend(
        current_price,
        ma21,
        ma200,
    )

    indicators[
        "short_trend"
    ] = classify_short_trend(
        current_price,
        ma21,
    )

    indicators[
        "long_trend"
    ] = classify_long_trend(
        current_price,
        ma200,
    )

    # ======================================================
    # PERFORMANCE
    # ======================================================

    performance = prepared_data.get(
        "performance",
        {}
    )

    if not isinstance(
        performance,
        dict,
    ):
        performance = {}

    performance_keys = [
        "daily_change",
        "daily_change_percent",
        "period_change",
        "period_change_percent",
        "period_high",
        "period_low",
        "distance_from_high",
        "distance_from_low",
        "volume",
        "average_volume",
    ]

    for key in performance_keys:

        value = performance.get(
            key,
            prepared_data.get(key),
        )

        indicators[key] = safe_float(
            value
        )

    # ======================================================
    # RANGE
    # ======================================================

    range_position = calculate_range_position(
        current_price,
        indicators.get("period_low"),
        indicators.get("period_high"),
    )

    indicators[
        "range_position"
    ] = range_position

    indicators[
        "range_status"
    ] = classify_range_position(
        range_position
    )

    # ======================================================
    # VOLUME
    # ======================================================

    volume_column = get_volume_column(
        history
    )

    # Prioriza valores do market.py
    volume = indicators.get(
        "volume"
    )

    average_volume = indicators.get(
        "average_volume"
    )

    # Fallback pelo histórico
    if volume is None and volume_column:

        volumes = get_numeric_series(
            history,
            volume_column,
        )

        if not volumes.empty:

            volume = safe_float(
                volumes.iloc[-1]
            )

    if average_volume is None and volume_column:

        volumes = get_numeric_series(
            history,
            volume_column,
        )

        if not volumes.empty:

            average_volume = safe_float(
                volumes.mean()
            )

    indicators["volume"] = volume
    indicators[
        "average_volume"
    ] = average_volume

    relative_volume = calculate_relative_volume(
        volume,
        average_volume,
    )

    indicators[
        "relative_volume"
    ] = relative_volume

    indicators[
        "volume_status"
    ] = classify_volume(
        relative_volume
    )

    return indicators


# ==========================================================
# TESTE LOCAL
# ==========================================================

if __name__ == "__main__":

    print(
        "Módulo indicators.py - Fase 3.0.7"
    )

    # Teste simples artificial
    dates = pd.date_range(
        end=pd.Timestamp.today(),
        periods=250,
        freq="B",
    )

    prices = np.linspace(
        30,
        45,
        250,
    )

    history = pd.DataFrame(
        {
            "Close": prices,
            "Volume": np.random.randint(
                1000000,
                5000000,
                250,
            ),
        },
        index=dates,
    )

    prepared_data = {
        "history": history,
        "performance": {
            "period_high": 45,
            "period_low": 30,
            "daily_change_percent": 0.01,
            "period_change_percent": 0.50,
        },
    }

    result = calculate_indicators(
        prepared_data
    )

    for key, value in result.items():

        print(
            f"{key}: {value}"
        )
