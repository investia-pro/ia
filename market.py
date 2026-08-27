"""
InvestIA PRO
Módulo de Mercado

Versão: v3.1.3
Fase Final: 3.1.3

Responsabilidades:
- Buscar dados de mercado
- Buscar histórico de preços
- Buscar informações fundamentalistas
- Preparar dados para indicadores e análise
- Calcular métricas de performance
- Padronizar estruturas retornadas ao app

Compatibilidade:
- app.py Fase 3.0.6+
- indicators.py Fase 3.0.6+
- analysis.py Fase 3.0.6+
"""

import time
import math
import traceback

import pandas as pd
import yfinance as yf


# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

DEFAULT_PERIOD = "1y"

VALID_PERIODS = [
    "1mo",
    "3mo",
    "6mo",
    "1y",
    "2y",
    "5y",
    "10y",
    "max",
]


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def safe_float(value, default=None):
    """
    Converte valores para float com segurança.

    Retorna default quando:
    - valor é None
    - valor não pode ser convertido
    - valor é NaN
    - valor é infinito
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


def normalize_asset(asset):
    """
    Normaliza o ativo para uso no Yahoo Finance.

    Exemplos:
        PETR4   -> PETR4.SA
        VALE3   -> VALE3.SA
        ITUB4   -> ITUB4.SA
        AAPL    -> AAPL
        BTC-USD -> BTC-USD
        ^BVSP   -> ^BVSP

    Observação:
    A normalização também existe no app.py.
    Esta função garante que market.py funcione
    independentemente de quem o chama.
    """

    if asset is None:
        return None

    asset = str(asset).strip().upper()

    if not asset:
        return None

    # Índices
    if asset.startswith("^"):
        return asset

    # Criptomoedas e pares
    if "-" in asset:
        return asset

    # Ativo já possui sufixo de mercado
    if "." in asset:
        return asset

    # Ações brasileiras:
    # PETR4, VALE3, ITUB4, BBAS3, BBDC4 etc.
    if len(asset) in (5, 6) and asset[-1].isdigit():
        return f"{asset}.SA"

    # Ativos internacionais
    return asset


def validate_period(period):
    """
    Valida o período solicitado.
    """

    if period in VALID_PERIODS:
        return period

    return DEFAULT_PERIOD


def clean_history(history):
    """
    Limpa e padroniza o DataFrame histórico.

    Remove:
    - linhas completamente vazias
    - índices duplicados
    - dados inválidos

    Também trata estruturas MultiIndex que podem
    ser retornadas pelo yfinance.
    """

    if history is None:
        return pd.DataFrame()

    if not isinstance(history, pd.DataFrame):
        try:
            history = pd.DataFrame(history)
        except Exception:
            return pd.DataFrame()

    if history.empty:
        return pd.DataFrame()

    history = history.copy()

    # ------------------------------------------------------
    # TRATAMENTO DE MULTIINDEX NAS COLUNAS
    # ------------------------------------------------------

    if isinstance(history.columns, pd.MultiIndex):

        try:
            history.columns = [
                column[0]
                if isinstance(column, tuple)
                else column
                for column in history.columns
            ]
        except Exception:
            history.columns = [
                str(column)
                for column in history.columns
            ]

    # ------------------------------------------------------
    # REMOVER LINHAS VAZIAS
    # ------------------------------------------------------

    history = history.dropna(
        how="all"
    )

    # ------------------------------------------------------
    # REMOVER ÍNDICES DUPLICADOS
    # ------------------------------------------------------

    try:

        history = history[
            ~history.index.duplicated(
                keep="last"
            )
        ]

    except Exception:
        pass

    # ------------------------------------------------------
    # ORDENAR POR DATA
    # ------------------------------------------------------

    try:

        history = history.sort_index()

    except Exception:
        pass

    # ------------------------------------------------------
    # NORMALIZAR COLUNAS IMPORTANTES
    # ------------------------------------------------------

    possible_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Adj Close",
        "Volume",
    ]

    for column in possible_columns:

        if column not in history.columns:
            continue

        try:

            history[column] = pd.to_numeric(
                history[column],
                errors="coerce",
            )

        except Exception:
            pass

    return history


def get_last_valid_value(
    series,
    default=None,
):
    """
    Retorna o último valor válido de uma série.
    """

    if series is None:
        return default

    try:

        cleaned = pd.Series(series).dropna()

        if cleaned.empty:
            return default

        return safe_float(
            cleaned.iloc[-1],
            default,
        )

    except Exception:
        return default


def get_first_valid_value(
    series,
    default=None,
):
    """
    Retorna o primeiro valor válido de uma série.
    """

    if series is None:
        return default

    try:

        cleaned = pd.Series(series).dropna()

        if cleaned.empty:
            return default

        return safe_float(
            cleaned.iloc[0],
            default,
        )

    except Exception:
        return default


def get_price_column(history):
    """
    Identifica a melhor coluna disponível para preço.
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


# ==========================================================
# BUSCA DE HISTÓRICO
# ==========================================================

def fetch_history(
    asset,
    period=DEFAULT_PERIOD,
    max_retries=3,
    retry_delay=2,
):
    """
    Busca o histórico de mercado com tentativas
    controladas.

    Não lança exceção para o chamador.
    Retorna DataFrame vazio em caso de falha.
    """

    asset = normalize_asset(asset)
    period = validate_period(period)

    if not asset:
        return pd.DataFrame()

    last_error = None

    for attempt in range(max_retries):

        try:

            ticker = yf.Ticker(asset)

            history = ticker.history(
                period=period,
                interval="1d",
                auto_adjust=False,
                actions=False,
            )

            history = clean_history(history)

            if not history.empty:

                return history

        except Exception as error:

            last_error = error

        # Evita sleep após última tentativa
        if attempt < max_retries - 1:

            time.sleep(
                retry_delay * (attempt + 1)
            )

    return pd.DataFrame()


# ==========================================================
# BUSCA DE FUNDAMENTOS
# ==========================================================

def fetch_fundamentals(
    asset,
):
    """
    Busca dados fundamentalistas básicos.

    O retorno é sempre um dicionário.

    Nem todos os ativos possuem fundamentos,
    principalmente índices e criptomoedas.
    """

    asset = normalize_asset(asset)

    if not asset:
        return {}

    try:

        ticker = yf.Ticker(asset)

        info = ticker.info

        if not isinstance(info, dict):
            return {}

    except Exception:

        return {}

    # ------------------------------------------------------
    # MAPEAMENTO DE CAMPOS
    # ------------------------------------------------------

    field_map = {

        "longName": "name",
        "shortName": "short_name",

        "sector": "sector",
        "industry": "industry",

        "marketCap": "market_cap",

        "trailingPE": "pe",
        "forwardPE": "forward_pe",

        "priceToBook": "price_to_book",

        "dividendYield": "dividend_yield",

        "returnOnEquity": "roe",

        "returnOnAssets": "roa",

        "profitMargins": "profit_margin",

        "operatingMargins": "operating_margin",

        "grossMargins": "gross_margin",

        "debtToEquity": "debt_to_equity",

        "currentRatio": "current_ratio",

        "quickRatio": "quick_ratio",

        "revenueGrowth": "revenue_growth",

        "earningsGrowth": "earnings_growth",

        "beta": "beta",

        "targetMeanPrice": "target_mean_price",

        "recommendationKey": "analyst_recommendation",

        "numberOfAnalystOpinions": "analyst_opinions",

        "fiftyTwoWeekHigh": "fifty_two_week_high",

        "fiftyTwoWeekLow": "fifty_two_week_low",

        "averageVolume": "average_volume",
    }

    fundamentals = {}

    for yahoo_key, output_key in field_map.items():

        try:

            value = info.get(yahoo_key)

            if value is not None:
                fundamentals[output_key] = value

        except Exception:
            continue

    return fundamentals


# ==========================================================
# BUSCA PRINCIPAL
# ==========================================================

def get_market_data(
    asset,
    period=DEFAULT_PERIOD,
):
    """
    Função principal de busca de dados.

    Retorna um dicionário padronizado.

    Estrutura:

    {
        "asset": "...",
        "period": "...",
        "history": DataFrame,
        "fundamentals": dict
    }
    """

    normalized_asset = normalize_asset(asset)
    period = validate_period(period)

    if not normalized_asset:

        return None

    history = fetch_history(
        normalized_asset,
        period=period,
    )

    if history.empty:

        return None

    fundamentals = fetch_fundamentals(
        normalized_asset
    )

    return {

        "asset": normalized_asset,

        "period": period,

        "history": history,

        "fundamentals": fundamentals,
    }


# ==========================================================
# MÉTRICAS DE PERFORMANCE
# ==========================================================

def calculate_performance_metrics(
    history,
):
    """
    Calcula métricas de performance a partir
    do histórico.

    Retorna:
    - preço atual
    - fechamento anterior
    - variação diária
    - variação do período
    - máxima
    - mínima
    - distância da máxima
    - distância da mínima
    - volume atual
    - volume médio
    """

    metrics = {

        "current_price": None,

        "previous_close": None,

        "daily_change": None,

        "daily_change_percent": None,

        "period_start_price": None,

        "period_change": None,

        "period_change_percent": None,

        "period_high": None,

        "period_low": None,

        "distance_from_high": None,

        "distance_from_low": None,

        "volume": None,

        "average_volume": None,
    }

    history = clean_history(history)

    if history.empty:
        return metrics

    price_column = get_price_column(history)

    if price_column is None:
        return metrics

    prices = pd.to_numeric(
        history[price_column],
        errors="coerce",
    ).dropna()

    if prices.empty:
        return metrics

    # ------------------------------------------------------
    # PREÇO ATUAL
    # ------------------------------------------------------

    current_price = safe_float(
        prices.iloc[-1]
    )

    metrics["current_price"] = current_price

    # ------------------------------------------------------
    # FECHAMENTO ANTERIOR
    # ------------------------------------------------------

    if len(prices) >= 2:

        previous_close = safe_float(
            prices.iloc[-2]
        )

        metrics[
            "previous_close"
        ] = previous_close

        if (
            current_price is not None
            and previous_close is not None
        ):

            daily_change = (
                current_price
                - previous_close
            )

            metrics[
                "daily_change"
            ] = daily_change

            if previous_close != 0:

                metrics[
                    "daily_change_percent"
                ] = (
                    daily_change
                    / previous_close
                )

    # ------------------------------------------------------
    # INÍCIO DO PERÍODO
    # ------------------------------------------------------

    period_start_price = safe_float(
        prices.iloc[0]
    )

    metrics[
        "period_start_price"
    ] = period_start_price

    if (
        current_price is not None
        and period_start_price is not None
    ):

        period_change = (
            current_price
            - period_start_price
        )

        metrics[
            "period_change"
        ] = period_change

        if period_start_price != 0:

            metrics[
                "period_change_percent"
            ] = (
                period_change
                / period_start_price
            )

    # ------------------------------------------------------
    # MÁXIMA E MÍNIMA
    # ------------------------------------------------------

    period_high = safe_float(
        prices.max()
    )

    period_low = safe_float(
        prices.min()
    )

    metrics[
        "period_high"
    ] = period_high

    metrics[
        "period_low"
    ] = period_low

    # ------------------------------------------------------
    # DISTÂNCIA DA MÁXIMA
    # ------------------------------------------------------

    if (
        current_price is not None
        and period_high is not None
        and period_high != 0
    ):

        metrics[
            "distance_from_high"
        ] = (
            current_price
            / period_high
            - 1
        )

    # ------------------------------------------------------
    # DISTÂNCIA DA MÍNIMA
    # ------------------------------------------------------

    if (
        current_price is not None
        and period_low is not None
        and period_low != 0
    ):

        metrics[
            "distance_from_low"
        ] = (
            current_price
            / period_low
            - 1
        )

    # ------------------------------------------------------
    # VOLUME
    # ------------------------------------------------------

    volume_columns = [
        "Volume",
        "volume",
    ]

    volume_column = None

    for column in volume_columns:

        if column in history.columns:

            volume_column = column
            break

    if volume_column is not None:

        volumes = pd.to_numeric(
            history[volume_column],
            errors="coerce",
        ).dropna()

        if not volumes.empty:

            metrics[
                "volume"
            ] = safe_float(
                volumes.iloc[-1]
            )

            metrics[
                "average_volume"
            ] = safe_float(
                volumes.mean()
            )

    return metrics


# ==========================================================
# PREPARAÇÃO DOS DADOS
# ==========================================================

def prepare_market_data(
    market_data,
):
    """
    Prepara os dados para consumo pelos módulos:

    - indicators.py
    - score.py
    - analysis.py
    - charts.py
    - app.py

    Mantém as chaves existentes para
    compatibilidade com versões anteriores.
    """

    if not isinstance(market_data, dict):

        return {}

    history = clean_history(
        market_data.get(
            "history"
        )
    )

    if history.empty:

        return {}

    fundamentals = market_data.get(
        "fundamentals",
        {}
    )

    if not isinstance(
        fundamentals,
        dict,
    ):

        fundamentals = {}

    performance = calculate_performance_metrics(
        history
    )

    current_price = performance.get(
        "current_price"
    )

    # ------------------------------------------------------
    # RETORNO PADRONIZADO
    # ------------------------------------------------------

    prepared_data = {

        # Identificação
        "asset": market_data.get(
            "asset"
        ),

        "period": market_data.get(
            "period"
        ),

        # Histórico
        "history": history,

        # Preço
        "price": current_price,

        "current_price": current_price,

        "close": current_price,

        # Performance
        "performance": performance,

        "daily_change": performance.get(
            "daily_change"
        ),

        "daily_change_percent": performance.get(
            "daily_change_percent"
        ),

        "period_change": performance.get(
            "period_change"
        ),

        "period_change_percent": performance.get(
            "period_change_percent"
        ),

        "period_high": performance.get(
            "period_high"
        ),

        "period_low": performance.get(
            "period_low"
        ),

        "distance_from_high": performance.get(
            "distance_from_high"
        ),

        "distance_from_low": performance.get(
            "distance_from_low"
        ),

        "volume": performance.get(
            "volume"
        ),

        "average_volume": performance.get(
            "average_volume"
        ),

        # Fundamentos
        "fundamentals": fundamentals,
    }

    return prepared_data


# ==========================================================
# FUNÇÃO DE RESUMO DE MERCADO
# ==========================================================

def get_market_summary(
    prepared_data,
):
    """
    Retorna um resumo simplificado dos dados
    de mercado.

    Esta função será utilizada nas próximas fases
    para comparação entre múltiplos ativos.
    """

    if not isinstance(
        prepared_data,
        dict,
    ):

        return {}

    performance = prepared_data.get(
        "performance",
        {}
    )

    if not isinstance(
        performance,
        dict,
    ):

        performance = {}

    return {

        "asset": prepared_data.get(
            "asset"
        ),

        "price": prepared_data.get(
            "current_price"
        ),

        "daily_change_percent": performance.get(
            "daily_change_percent"
        ),

        "period_change_percent": performance.get(
            "period_change_percent"
        ),

        "period_high": performance.get(
            "period_high"
        ),

        "period_low": performance.get(
            "period_low"
        ),

        "distance_from_high": performance.get(
            "distance_from_high"
        ),

        "distance_from_low": performance.get(
            "distance_from_low"
        ),

        "volume": performance.get(
            "volume"
        ),

        "average_volume": performance.get(
            "average_volume"
        ),
    }


# ==========================================================
# TESTE LOCAL
# ==========================================================

if __name__ == "__main__":

    test_asset = "PETR4"

    print(
        f"Testando ativo: {test_asset}"
    )

    data = get_market_data(
        test_asset,
        period="1y",
    )

    if data is None:

        print(
            "Não foi possível obter dados."
        )

    else:

        prepared = prepare_market_data(
            data
        )

        print(
            "\nDados preparados:"
        )

        print(
            list(prepared.keys())
        )

        print(
            "\nResumo de mercado:"
        )

        print(
            get_market_summary(
                prepared
            )
        )
