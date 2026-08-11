"""
InvestIA PRO
Módulo de dados de mercado

Versão: v0.6
Fase: 2.3.1 - Estabilização do Market Data
"""

import yfinance as yf
import streamlit as st
import pandas as pd


# ==========================================================
# NORMALIZAÇÃO DO ATIVO
# ==========================================================

def normalize_asset(asset):
    """
    Normaliza o código do ativo.

    Exemplo:
        PETR4 -> PETR4.SA
        PETR4.SA -> PETR4.SA
    """

    if asset is None:
        return None

    asset = str(asset).strip().upper()

    if not asset:
        return None

    if asset.endswith(".SA"):
        return asset

    return f"{asset}.SA"


# ==========================================================
# BUSCA DOS DADOS DE MERCADO
# ==========================================================

@st.cache_data(ttl=300)
def get_market_data(
    asset,
    period="1y",
):
    """
    Busca dados históricos do ativo.

    Retorna um dicionário no formato:

    {
        "asset": "PETR4",
        "ticker": "PETR4.SA",
        "history": DataFrame,
        "price": float
    }

    Esse formato é utilizado pelo indicators.py.
    """

    ticker_symbol = normalize_asset(
        asset
    )

    if ticker_symbol is None:
        return None

    try:

        # ==================================================
        # YAHOO FINANCE
        # ==================================================

        ticker = yf.Ticker(
            ticker_symbol
        )

        data = ticker.history(
            period=period,
            auto_adjust=False,
        )

        # ==================================================
        # VALIDAÇÃO
        # ==================================================

        if data is None:
            return None

        if data.empty:
            return None

        # ==================================================
        # TRATAMENTO DE MULTIINDEX
        # ==================================================

        if isinstance(
            data.columns,
            pd.MultiIndex,
        ):

            data.columns = [
                column[0]
                if isinstance(
                    column,
                    tuple,
                )
                else column
                for column in data.columns
            ]

        # ==================================================
        # VERIFICA COLUNA CLOSE
        # ==================================================

        if "Close" not in data.columns:
            return None

        # ==================================================
        # LIMPEZA
        # ==================================================

        data = data.copy()

        data = data.dropna(
            subset=["Close"]
        )

        if data.empty:
            return None

        # ==================================================
        # CONVERSÃO NUMÉRICA
        # ==================================================

        for column in data.columns:

            data[column] = pd.to_numeric(
                data[column],
                errors="coerce",
            )

        data = data.dropna(
            subset=["Close"]
        )

        if data.empty:
            return None

        # ==================================================
        # ORDENAÇÃO
        # ==================================================

        data = data.sort_index()

        # ==================================================
        # ÚLTIMO PREÇO
        # ==================================================

        price = data[
            "Close"
        ].iloc[-1]

        if pd.isna(price):
            return None

        price = float(price)

        # ==================================================
        # RETORNO
        # ==================================================

        return {

            "asset": str(asset)
            .strip()
            .upper(),

            "ticker": ticker_symbol,

            "history": data,

            "price": price,
        }

    except Exception as error:

        print(
            f"Erro ao buscar "
            f"{ticker_symbol}: {error}"
        )

        return None


# ==========================================================
# ÚLTIMO PREÇO
# ==========================================================

def get_current_price(
    market_data
):
    """
    Retorna o último preço do ativo.

    Aceita o dicionário retornado
    por get_market_data().
    """

    if market_data is None:
        return None

    # ------------------------------------------------------
    # Formato atual
    # ------------------------------------------------------

    if isinstance(
        market_data,
        dict,
    ):

        if "price" in market_data:

            try:

                return float(
                    market_data["price"]
                )

            except (
                TypeError,
                ValueError,
            ):

                pass

        if "history" in market_data:

            history = market_data[
                "history"
            ]

            if (
                history is not None
                and not history.empty
                and "Close" in history.columns
            ):

                try:

                    return float(
                        history[
                            "Close"
                        ].iloc[-1]
                    )

                except (
                    TypeError,
                    ValueError,
                    IndexError,
                ):

                    return None

    # ------------------------------------------------------
    # Compatibilidade com DataFrame
    # ------------------------------------------------------

    if isinstance(
        market_data,
        pd.DataFrame,
    ):

        if (
            not market_data.empty
            and "Close" in market_data.columns
        ):

            try:

                return float(
                    market_data[
                        "Close"
                    ].iloc[-1]
                )

            except (
                TypeError,
                ValueError,
                IndexError,
            ):

                return None

    return None


# ==========================================================
# PREPARAÇÃO DOS DADOS
# ==========================================================

def prepare_market_data(
    data
):
    """
    Padroniza os dados de mercado.

    Mantém o histórico no campo "history"
    para utilização pelo indicators.py.
    """

    if data is None:
        return None

    # ======================================================
    # SE JÁ FOR O FORMATO PADRONIZADO
    # ======================================================

    if isinstance(
        data,
        dict,
    ):

        if "history" not in data:
            return None

        history = data[
            "history"
        ]

        if history is None:
            return None

        if history.empty:
            return None

        price = get_current_price(
            data
        )

        if price is None:
            return None

        result = data.copy()

        result["price"] = price

        return result

    # ======================================================
    # COMPATIBILIDADE COM DATAFRAME
    # ======================================================

    if isinstance(
        data,
        pd.DataFrame,
    ):

        if data.empty:
            return None

        if "Close" not in data.columns:
            return None

        price = get_current_price(
            data
        )

        if price is None:
            return None

        return {

            "history": data,

            "price": price,
        }

    return None
