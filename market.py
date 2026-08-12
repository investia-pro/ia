"""
InvestIA PRO
Market Data

Versão: v0.6
Fase: 2.6.3 - Estabilidade do Market Data
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

def normalize_ticker(asset):
    """
    Normaliza o código do ativo.

    Exemplos:

    PETR4 -> PETR4.SA
    VALE3 -> VALE3.SA
    ITUB4 -> ITUB4.SA
    PETR4.SA -> PETR4.SA
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

    if not asset.endswith(".SA"):
        asset = f"{asset}.SA"

    return asset


# ==========================================================
# DOWNLOAD DOS DADOS
# ==========================================================

def _download_market_data(
    ticker_symbol,
    period,
):
    """
    Faz a consulta ao Yahoo Finance.

    Esta função não possui cache.
    O cache fica na função pública
    get_market_data().
    """

    last_error = None

    for attempt in range(
        MAX_RETRIES
    ):

        try:

            ticker = yf.Ticker(
                ticker_symbol
            )

            data = ticker.history(
                period=period,
                auto_adjust=False,
            )

            # ----------------------------------------------
            # VALIDAÇÃO
            # ----------------------------------------------

            if data is None:

                raise ValueError(
                    "Yahoo Finance retornou None."
                )

            if data.empty:

                raise ValueError(
                    "Yahoo Finance retornou "
                    "um histórico vazio."
                )

            # ----------------------------------------------
            # NORMALIZAÇÃO DO INDEX
            # ----------------------------------------------

            if not isinstance(
                data.index,
                pd.DatetimeIndex,
            ):

                data.index = pd.to_datetime(
                    data.index
                )

            # ----------------------------------------------
            # LIMPEZA
            # ----------------------------------------------

            data = data.copy()

            data.dropna(
                how="all",
                inplace=True,
            )

            if data.empty:

                raise ValueError(
                    "Histórico ficou vazio "
                    "após limpeza."
                )

            return data

        except Exception as error:

            last_error = error

            error_text = str(
                error
            ).lower()

            # ----------------------------------------------
            # RATE LIMIT
            # ----------------------------------------------

            if (
                "rate" in error_text
                or "too many requests"
                in error_text
                or "ratelimit" in error_text
            ):

                # Não fazemos várias requisições
                # imediatamente.

                if attempt < MAX_RETRIES - 1:

                    time.sleep(
                        3
                        * (
                            attempt + 1
                        )
                    )

                    continue

                break

            # ----------------------------------------------
            # OUTROS ERROS
            # ----------------------------------------------

            if attempt < MAX_RETRIES - 1:

                time.sleep(1)

                continue

    # ======================================================
    # FALHA FINAL
    # ======================================================

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
    Obtém dados históricos do ativo.

    Utiliza cache para evitar requisições
    repetidas ao Yahoo Finance.
    """

    ticker_symbol = normalize_ticker(
        asset
    )

    if ticker_symbol is None:

        return None

    data = _download_market_data(
        ticker_symbol,
        period,
    )

    if data is None:

        return None

    return data


# ==========================================================
# PREPARAÇÃO DOS DADOS
# ==========================================================

def prepare_market_data(
    market_data
):
    """
    Prepara os dados para os módulos
    de indicadores e análise.

    Retorno:

    {
        "history": DataFrame
    }
    """

    if market_data is None:

        return None

    if not isinstance(
        market_data,
        pd.DataFrame,
    ):

        return None

    if market_data.empty:

        return None

    history = market_data.copy()

    # ======================================================
    # LIMPEZA
    # ======================================================

    history.dropna(
        how="all",
        inplace=True,
    )

    if history.empty:

        return None

    # ======================================================
    # GARANTE COLUNAS IMPORTANTES
    # ======================================================

    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    available_columns = [
        column
        for column in required_columns
        if column in history.columns
    ]

    if "Close" not in history.columns:

        return None

    # ======================================================
    # CONVERSÃO NUMÉRICA
    # ======================================================

    for column in available_columns:

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
    # RETORNO PADRONIZADO
    # ======================================================

    return {
        "history": history,
    }


# ==========================================================
# PREÇO ATUAL
# ==========================================================

def get_current_price(
    market_data
):
    """
    Obtém o preço mais recente disponível.
    """

    if market_data is None:

        return None

    # ======================================================
    # ESTRUTURA PADRONIZADA
    # ======================================================

    if isinstance(
        market_data,
        dict,
    ):

        history = market_data.get(
            "history"
        )

    else:

        history = market_data

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

    close = history["Close"].dropna()

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
# ÚLTIMO PREÇO
# ==========================================================

def get_last_close(
    market_data
):
    """
    Alias para get_current_price().
    """

    return get_current_price(
        market_data
    )


# ==========================================================
# LIMPAR CACHE
# ==========================================================

def clear_market_cache():
    """
    Limpa o cache dos dados de mercado.
    """

    try:

        get_market_data.clear()

    except Exception:

        pass
