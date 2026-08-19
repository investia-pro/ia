"""
InvestIA PRO
Módulo de dados de mercado

Versão: v0.6
Fase: 2.9.7 - Estabilidade do Market Data
"""

import time

import pandas as pd
import yfinance as yf


# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

MAX_RETRIES = 3

RETRY_DELAY = 3


# ==========================================================
# NORMALIZAÇÃO
# ==========================================================

def normalize_asset(asset):
    """
    Normaliza o código do ativo.
    """

    if asset is None:
        return ""

    return (
        str(asset)
        .strip()
        .upper()
        .replace(" ", "")
    )


def normalize_yahoo_ticker(asset):
    """
    Converte o código informado para o formato
    utilizado pelo Yahoo Finance.
    """

    asset = normalize_asset(asset)

    if not asset:
        return ""

    # Ativos brasileiros
    if (
        "." not in asset
        and asset[-1:].isdigit()
    ):

        return f"{asset}.SA"

    return asset


# ==========================================================
# VALIDAÇÃO DO HISTÓRICO
# ==========================================================

def validate_history(history):
    """
    Valida o DataFrame histórico retornado
    pelo Yahoo Finance.
    """

    if history is None:
        return False

    if not isinstance(
        history,
        pd.DataFrame,
    ):
        return False

    if history.empty:
        return False

    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    available_columns = set(
        history.columns
    )

    # Alguns retornos do yfinance podem
    # apresentar estrutura diferente.
    # Neste caso, Close continua sendo
    # indispensável.

    if "Close" not in available_columns:
        return False

    return True


# ==========================================================
# LIMPEZA DO HISTÓRICO
# ==========================================================

def clean_history(history):
    """
    Limpa e normaliza o histórico.
    """

    if not validate_history(
        history
    ):

        return pd.DataFrame()

    data = history.copy()

    # ------------------------------------------------------
    # MultiIndex
    # ------------------------------------------------------

    if isinstance(
        data.columns,
        pd.MultiIndex,
    ):

        try:

            data.columns = [
                column[0]
                if isinstance(
                    column,
                    tuple,
                )
                else column
                for column in data.columns
            ]

        except Exception:

            pass

    # ------------------------------------------------------
    # Índice
    # ------------------------------------------------------

    try:

        data = data.sort_index()

    except Exception:

        pass

    # ------------------------------------------------------
    # Remover duplicidades
    # ------------------------------------------------------

    try:

        data = data[
            ~data.index.duplicated(
                keep="last"
            )
        ]

    except Exception:

        pass

    # ------------------------------------------------------
    # Numericidade
    # ------------------------------------------------------

    numeric_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Adj Close",
        "Volume",
    ]

    for column in numeric_columns:

        if column in data.columns:

            try:

                data[column] = pd.to_numeric(
                    data[column],
                    errors="coerce",
                )

            except Exception:

                pass

    # ------------------------------------------------------
    # Remover linhas sem fechamento
    # ------------------------------------------------------

    if "Close" in data.columns:

        data = data.dropna(
            subset=["Close"]
        )

    return data


# ==========================================================
# BUSCA DO HISTÓRICO
# ==========================================================

def _download_history(
    ticker_symbol,
    period,
):
    """
    Executa a consulta ao Yahoo Finance.
    """

    ticker = yf.Ticker(
        ticker_symbol
    )

    history = ticker.history(
        period=period,
        interval="1d",
        auto_adjust=False,
    )

    return history


# ==========================================================
# BUSCA PRINCIPAL
# ==========================================================

def get_market_data(
    asset,
    period="1y",
):
    """
    Busca dados do mercado.

    Retorno:

    {
        "asset": "PETR4",
        "ticker": "PETR4.SA",
        "history": DataFrame
    }
    """

    original_asset = normalize_asset(
        asset
    )

    if not original_asset:

        return None

    ticker_symbol = normalize_yahoo_ticker(
        original_asset
    )

    if not ticker_symbol:

        return None

    last_error = None

    # ======================================================
    # TENTATIVAS
    # ======================================================

    for attempt in range(
        1,
        MAX_RETRIES + 1,
    ):

        try:

            history = _download_history(
                ticker_symbol,
                period,
            )

            history = clean_history(
                history
            )

            if validate_history(
                history
            ):

                return {

                    "asset":
                        original_asset,

                    "ticker":
                        ticker_symbol,

                    "history":
                        history,
                }

            last_error = ValueError(
                "Yahoo Finance retornou "
                "histórico vazio ou inválido."
            )

        except Exception as error:

            last_error = error

            # --------------------------------------------------
            # Retry progressivo
            # --------------------------------------------------

            if attempt < MAX_RETRIES:

                time.sleep(
                    RETRY_DELAY * attempt
                )

    # ======================================================
    # FALHA
    # ======================================================

    return None


# ==========================================================
# PREPARAÇÃO
# ==========================================================

def prepare_market_data(
    market_data,
):
    """
    Prepara os dados para os demais módulos.

    Garante a existência de:

    asset
    ticker
    history
    price
    """

    if market_data is None:

        return None

    # ------------------------------------------------------
    # Caso já seja o formato esperado
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # Compatibilidade com DataFrame
    # ------------------------------------------------------

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
    # HISTÓRICO
    # ======================================================

    history = clean_history(
        history
    )

    if not validate_history(
        history
    ):

        return None

    # ======================================================
    # PREÇO
    # ======================================================

    try:

        close_series = history[
            "Close"
        ].dropna()

        if close_series.empty:

            return None

        price = float(
            close_series.iloc[-1]
        )

    except Exception:

        return None

    if asset is None:

        asset = ticker or ""

        if isinstance(
            asset,
            str,
        ):

            asset = asset.replace(
                ".SA",
                "",
            )

    # ======================================================
    # RETORNO PADRONIZADO
    # ======================================================

    return {

        "asset":
            normalize_asset(
                asset
            ),

        "ticker":
            ticker,

        "history":
            history,

        "price":
            price,
    }


# ==========================================================
# PREÇO ATUAL
# ==========================================================

def get_current_price(
    prepared_data,
):
    """
    Retorna o preço mais recente.
    """

    if prepared_data is None:

        return None

    # ------------------------------------------------------
    # Primeiro tenta preço já calculado
    # ------------------------------------------------------

    if isinstance(
        prepared_data,
        dict,
    ):

        price = prepared_data.get(
            "price"
        )

        if price is not None:

            try:

                return float(
                    price
                )

            except (
                TypeError,
                ValueError,
            ):

                pass

    # ------------------------------------------------------
    # Depois utiliza histórico
    # ------------------------------------------------------

    if not isinstance(
        prepared_data,
        dict,
    ):

        return None

    history = prepared_data.get(
        "history"
    )

    if not validate_history(
        history
    ):

        return None

    try:

        close = (
            history["Close"]
            .dropna()
        )

        if close.empty:

            return None

        return float(
            close.iloc[-1]
        )

    except Exception:

        return None
