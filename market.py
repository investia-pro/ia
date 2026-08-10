"""
InvestIA PRO
Camada de Dados de Mercado

Versão: v0.5.3 Stable
"""

import logging

import pandas as pd
import streamlit as st
import yfinance as yf

from config import (
    CACHE_TTL,
    MARKET_SUFFIX,
    DEFAULT_PERIOD,
)


# ==========================================================
# Logger
# ==========================================================

logger = logging.getLogger(__name__)


# ==========================================================
# Validação
# ==========================================================

def _validate_market_data(data):
    """
    Valida se o DataFrame possui dados utilizáveis.
    """

    if data is None:
        return False

    if data.empty:
        return False

    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    return all(
        column in data.columns
        for column in required_columns
    )


# ==========================================================
# Download dos dados
# ==========================================================

@st.cache_data(ttl=CACHE_TTL)
def get_market_data(
    asset: str,
    period: str = DEFAULT_PERIOD,
):
    """
    Busca dados históricos do ativo.

    Parameters
    ----------
    asset : str
        Código do ativo, exemplo: PETR4.

    period : str
        Período histórico, exemplo: 1y.

    Returns
    -------
    dict | None

    Estrutura:

    {
        "asset": "PETR4",
        "price": 38.50,
        "history": DataFrame
    }
    """

    if not asset:
        raise ValueError(
            "O código do ativo não foi informado."
        )

    asset = asset.strip().upper()

    # ------------------------------------------------------
    # Monta ticker brasileiro
    # ------------------------------------------------------

    if asset.endswith(MARKET_SUFFIX):
        ticker_symbol = asset
        clean_asset = asset.replace(
            MARKET_SUFFIX,
            "",
        )
    else:
        ticker_symbol = (
            f"{asset}{MARKET_SUFFIX}"
        )
        clean_asset = asset

    # ------------------------------------------------------
    # Busca dados
    # ------------------------------------------------------

    try:

        logger.info(
            "Buscando dados de %s",
            ticker_symbol,
        )

        data = yf.download(
            ticker_symbol,
            period=period,
            interval="1d",
            auto_adjust=True,
            progress=False,
            threads=False,
        )

    except Exception as error:

        logger.exception(
            "Erro ao consultar Yahoo Finance: %s",
            error,
        )

        raise RuntimeError(
            f"Erro ao consultar dados de "
            f"{ticker_symbol}: {error}"
        ) from error

    # ------------------------------------------------------
    # Verifica retorno
    # ------------------------------------------------------

    if data is None or data.empty:

        raise ValueError(
            f"Nenhum dado encontrado para "
            f"{ticker_symbol}."
        )

    # ------------------------------------------------------
    # Trata MultiIndex
    # ------------------------------------------------------

    if isinstance(
        data.columns,
        pd.MultiIndex,
    ):

        try:

            data.columns = (
                data.columns
                .get_level_values(0)
            )

        except Exception:

            data.columns = [
                column[0]
                if isinstance(column, tuple)
                else column
                for column in data.columns
            ]

    # ------------------------------------------------------
    # Remove linhas inválidas
    # ------------------------------------------------------

    data = data.dropna(
        subset=["Close"]
    )

    if data.empty:

        raise ValueError(
            f"Os dados retornados para "
            f"{ticker_symbol} não possuem "
            f"preços válidos."
        )

    # ------------------------------------------------------
    # Ordenação
    # ------------------------------------------------------

    data = data.sort_index()

    # ------------------------------------------------------
    # Último preço
    # ------------------------------------------------------

    price = float(
        data["Close"].iloc[-1]
    )

    # ------------------------------------------------------
    # Resultado padronizado
    # ------------------------------------------------------

    return {
        "asset": clean_asset,
        "price": price,
        "history": data,
    }
