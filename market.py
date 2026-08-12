"""
InvestIA PRO
Market Data

Versão: v0.6
Fase: 2.6.3 - Estabilidade do Market Data
Correção: suporte à chave "asset"
"""

import time

import pandas as pd
import streamlit as st
import yfinance as yf


# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

MAX_RETRIES = 2

CACHE_TTL = 900  # 15 minutos


# ==========================================================
# NORMALIZAÇÃO DO ATIVO
# ==========================================================

def normalize_asset(asset):
    """
    Normaliza o código do ativo.

    Exemplos:

    PETR4     -> PETR4
    PETR4.SA  -> PETR4
    VALE3     -> VALE3
    ITUB4     -> ITUB4
    """

    if asset is None:
        return None

    asset = (
        str(asset)
        .strip()
        .upper()
        .replace(" ", "")
    )

    if not asset:
        return None

    if asset.endswith(".SA"):
        asset = asset[:-3]

    return asset


def normalize_ticker(asset):
    """
    Converte o ativo para o ticker utilizado
    pelo Yahoo Finance.
    """

    normalized = normalize_asset(asset)

    if normalized is None:
        return None

    return f"{normalized}.SA"


# ==========================================================
# DOWNLOAD DOS DADOS
# ==========================================================

def _download_market_data(
    ticker_symbol,
    period,
):
    """
    Faz a consulta ao Yahoo Finance.
    """

    for attempt in range(MAX_RETRIES):

        try:

            ticker = yf.Ticker(
                ticker_symbol
            )

            data = ticker.history(
                period=period,
                auto_adjust=False,
            )

            # ------------------------------------------------
            # VALIDAÇÃO
            # ------------------------------------------------

            if data is None:

                raise ValueError(
                    "Yahoo Finance retornou None."
                )

            if data.empty:

                raise ValueError(
                    "Yahoo Finance retornou "
                    "um histórico vazio."
                )

            # ------------------------------------------------
            # INDEX
            # ------------------------------------------------

            if not isinstance(
                data.index,
                pd.DatetimeIndex,
            ):

                data.index = pd.to_datetime(
                    data.index
                )

            # ------------------------------------------------
            # LIMPEZA
            # ------------------------------------------------

            data = data.copy()

            data.dropna(
                how="all",
                inplace=True,
            )

            if data.empty:

                raise ValueError(
                    "Histórico vazio após limpeza."
                )

            return data

        except Exception as error:

            error_text = str(
                error
            ).lower()

            # ================================================
            # RATE LIMIT
            # ================================================

            is_rate_limit = (
                "rate" in error_text
                or
                "too many requests"
                in error_text
                or
                "ratelimit"
                in error_text
            )

            if is_rate_limit:

                if attempt < MAX_RETRIES - 1:

                    time.sleep(
                        3 * (attempt + 1)
                    )

                    continue

                return None

            # ================================================
            # OUTROS ERROS
            # ================================================

            if attempt < MAX_RETRIES - 1:

                time.sleep(1)

                continue

            return None

    return None


# ==========================================================
# OBTENÇÃO DOS DADOS
# ==========================================================

@st.cache_data(
    ttl=CACHE_TTL,
    show_spinner=False,
)
def get_market_data(
    asset,
    period="1y",
):
    """
    Obtém os dados do mercado.

    Retorna um dicionário contendo:

    {
        "asset": "PETR4",
        "ticker": "PETR4.SA",
        "history": DataFrame
    }
    """

    normalized_asset = normalize_asset(
        asset
    )

    if normalized_asset is None:

        return None

    ticker_symbol = normalize_ticker(
        normalized_asset
    )

    if ticker_symbol is None:

        return None

    history = _download_market_data(
        ticker_symbol,
        period,
    )

    if history is None:

        return None

    return {
        "asset": normalized_asset,
        "ticker": ticker_symbol,
        "history": history,
    }


# ==========================================================
# PREPARAÇÃO DOS DADOS
# ==========================================================

def prepare_market_data(
    market_data
):
    """
    Prepara os dados para os módulos
    de indicadores e análise.

    Mantém a estrutura esperada
    pelo indicators.py.
    """

    if market_data is None:

        return None

    # ======================================================
    # NOVA ESTRUTURA
    # ======================================================

    if isinstance(
        market_data,
        dict,
    ):

        asset = market_data.get(
            "asset"
        )

        ticker = market_data.get(
            "ticker"
        )

        history = market_data.get(
            "history"
        )

    # ======================================================
    # COMPATIBILIDADE COM DATAFRAME
    # ======================================================

    elif isinstance(
        market_data,
        pd.DataFrame,
    ):

        asset = None

        ticker = None

        history = market_data

    else:

        return None

    # ======================================================
    # VALIDAÇÃO
    # ======================================================

    if history is None:

        return None

    if not isinstance(
        history,
        pd.DataFrame,
    ):

        return None

    if history.empty:

        return None

    # ======================================================
    # CÓDIGO DO ATIVO
    # ======================================================

    if asset is None:

        asset = "UNKNOWN"

    asset = normalize_asset(
        asset
    )

    # ======================================================
    # LIMPEZA
    # ======================================================

    history = history.copy()

    history.dropna(
        how="all",
        inplace=True,
    )

    if history.empty:

        return None

    # ======================================================
    # COLUNAS NECESSÁRIAS
    # ======================================================

    if "Close" not in history.columns:

        return None

    # ======================================================
    # CONVERSÃO NUMÉRICA
    # ======================================================

    numeric_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Adj Close",
        "Volume",
    ]

    for column in numeric_columns:

        if column in history.columns:

            history[column] = pd.to_numeric(
                history[column],
                errors="coerce",
            )

    # ======================================================
    # REMOVE LINHAS SEM FECHAMENTO
    # ======================================================

    history.dropna(
        subset=["Close"],
        inplace=True,
    )

    if history.empty:

        return None

    # ======================================================
    # RETORNO
    # ======================================================

    return {
        "asset": asset,
        "ticker": ticker,
        "history": history,
    }


# ==========================================================
# PREÇO ATUAL
# ==========================================================

def get_current_price(
    market_data
):
    """
    Obtém o preço de fechamento mais recente.
    """

    if market_data is None:

        return None

    # ======================================================
    # DICIONÁRIO
    # ======================================================

    if isinstance(
        market_data,
        dict,
    ):

        history = market_data.get(
            "history"
        )

    # ======================================================
    # DATAFRAME
    # ======================================================

    elif isinstance(
        market_data,
        pd.DataFrame,
    ):

        history = market_data

    else:

        return None

    # ======================================================
    # VALIDAÇÃO
    # ======================================================

    if history is None:

        return None

    if not isinstance(
        history,
        pd.DataFrame,
    ):

        return None

    if history.empty:

        return None

    if "Close" not in history.columns:

        return None

    # ======================================================
    # PREÇO
    # ======================================================

    close = history[
        "Close"
    ].dropna()

    if close.empty:

        return None

    try:

        return float(
            close.iloc[-1]
        )

    except (
        TypeError,
        ValueError,
    ):

        return None


# ==========================================================
# ALIAS
# ==========================================================

def get_last_close(
    market_data
):
    """
    Retorna o último fechamento.
    """

    return get_current_price(
        market_data
    )


# ==========================================================
# LIMPEZA DO CACHE
# ==========================================================

def clear_market_cache():
    """
    Limpa o cache dos dados de mercado.
    """

    try:

        get_market_data.clear()

    except Exception:

        pass
