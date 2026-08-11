"""
InvestIA PRO
Módulo de dados de mercado

Versão: v0.6
Fase: Diagnóstico do Market Data
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

    Exemplos:

    PETR4
    ↓
    PETR4.SA

    PETR4.SA
    ↓
    PETR4.SA
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

    Retorno esperado:

    {
        "asset": "PETR4",
        "ticker": "PETR4.SA",
        "history": DataFrame,
        "price": float
    }

    O campo "history" é obrigatório para o
    indicators.py atual.
    """

    ticker_symbol = normalize_asset(
        asset
    )

    if ticker_symbol is None:

        st.error(
            "Código do ativo inválido."
        )

        return None

    try:

        # ==================================================
        # INFORMAÇÕES DO ATIVO
        # ==================================================

        ticker = yf.Ticker(
            ticker_symbol
        )

        # ==================================================
        # HISTÓRICO
        # ==================================================

        data = ticker.history(
            period=period,
            auto_adjust=False,
        )

        # ==================================================
        # VERIFICAÇÃO DO RETORNO
        # ==================================================

        if data is None:

            st.error(
                f"O Yahoo Finance não retornou "
                f"dados para {ticker_symbol}."
            )

            return None

        if data.empty:

            st.error(
                f"O histórico de {ticker_symbol} "
                f"retornou vazio."
            )

            st.info(
                "Ticker consultado: "
                f"{ticker_symbol}"
            )

            st.info(
                "Período solicitado: "
                f"{period}"
            )

            return None

        # ==================================================
        # MULTIINDEX
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
        # VERIFICA CLOSE
        # ==================================================

        if "Close" not in data.columns:

            st.error(
                "A resposta do Yahoo Finance "
                "não contém a coluna Close."
            )

            st.write(
                "Colunas recebidas:"
            )

            st.write(
                list(data.columns)
            )

            return None

        # ==================================================
        # CÓPIA DOS DADOS
        # ==================================================

        data = data.copy()

        # ==================================================
        # CONVERSÃO NUMÉRICA
        # ==================================================

        numeric_columns = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]

        for column in numeric_columns:

            if column in data.columns:

                data[column] = pd.to_numeric(
                    data[column],
                    errors="coerce",
                )

        # ==================================================
        # REMOVE LINHAS INVÁLIDAS
        # ==================================================

        data = data.dropna(
            subset=[
                "Close"
            ]
        )

        if data.empty:

            st.error(
                "Após a limpeza dos dados, "
                "não restaram preços válidos."
            )

            return None

        # ==================================================
        # ORDENAÇÃO
        # ==================================================

        data = data.sort_index()

        # ==================================================
        # PREÇO ATUAL
        # ==================================================

        price = data[
            "Close"
        ].iloc[-1]

        if pd.isna(price):

            st.error(
                "Não foi possível determinar "
                "o último preço."
            )

            return None

        price = float(
            price
        )

        # ==================================================
        # RETORNO PADRONIZADO
        # ==================================================

        result = {

            "asset":
                str(asset)
                .strip()
                .upper(),

            "ticker":
                ticker_symbol,

            "history":
                data,

            "price":
                price,
        }

        return result

    except Exception as error:

        # ==================================================
        # DIAGNÓSTICO
        # ==================================================

        st.error(
            f"Erro ao consultar "
            f"{ticker_symbol}"
        )

        st.exception(
            error
        )

        return None


# ==========================================================
# ÚLTIMO PREÇO
# ==========================================================

def get_current_price(
    market_data,
):
    """
    Retorna o último preço disponível.
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

        # --------------------------------------------------
        # Preço já calculado
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Histórico
        # --------------------------------------------------

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

    # ======================================================
    # DATAFRAME
    # ======================================================

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
    data,
):
    """
    Padroniza os dados de mercado.

    Mantém o campo history para o
    indicators.py.
    """

    if data is None:
        return None

    # ======================================================
    # DICIONÁRIO
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

        if "Close" not in history.columns:

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
    # DATAFRAME
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

            "history":
                data,

            "price":
                price,
        }

    return None
