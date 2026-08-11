"""
InvestIA PRO
Módulo de dados de mercado

Versão: v0.6
Fase: Estabilização do Market Data
"""

import yfinance as yf
import streamlit as st
import pandas as pd


# ==========================================================
# NORMALIZAÇÃO DO ATIVO
# ==========================================================

def normalize_asset(asset):
    """
    Normaliza o código do ativo para utilização no Yahoo Finance.
    """

    if asset is None:
        return None

    asset = str(asset).strip().upper()

    if not asset:
        return None

    # Evita adicionar .SA duas vezes
    if asset.endswith(".SA"):
        return asset

    return f"{asset}.SA"


# ==========================================================
# BUSCA DOS DADOS
# ==========================================================

@st.cache_data(ttl=300)
def get_market_data(
    asset,
    period="1y",
):
    """
    Busca dados históricos do ativo.

    Parâmetros
    ----------
    asset : str
        Código do ativo, exemplo: PETR4.

    period : str
        Período do histórico.

    Retorno
    -------
    pandas.DataFrame ou None
    """

    ticker_symbol = normalize_asset(
        asset
    )

    if ticker_symbol is None:
        return None

    try:

        # ==================================================
        # PRIMEIRA TENTATIVA
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
        # NORMALIZAÇÃO DAS COLUNAS
        # ==================================================

        # Alguns retornos do Yahoo podem apresentar
        # MultiIndex nas colunas.

        if isinstance(
            data.columns,
            pd.MultiIndex,
        ):

            data.columns = [
                column[0]
                if isinstance(column, tuple)
                else column
                for column in data.columns
            ]

        # ==================================================
        # COLUNAS NECESSÁRIAS
        # ==================================================

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
            if column in data.columns
        ]

        if "Close" not in available_columns:
            return None

        # Mantém somente as colunas disponíveis
        data = data[
            available_columns
        ].copy()

        # ==================================================
        # LIMPEZA
        # ==================================================

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

        return data

    except Exception as error:

        # Não esconder completamente o erro.
        # O Streamlit poderá mostrar a causa durante
        # a estabilização.

        print(
            f"Erro ao buscar {ticker_symbol}: {error}"
        )

        return None


# ==========================================================
# ÚLTIMO PREÇO
# ==========================================================

def get_current_price(data):
    """
    Retorna o último preço disponível.
    """

    if data is None:
        return None

    if data.empty:
        return None

    if "Close" not in data.columns:
        return None

    try:

        price = data["Close"].iloc[-1]

        if pd.isna(price):
            return None

        return float(price)

    except (
        TypeError,
        ValueError,
        IndexError,
    ):

        return None


# ==========================================================
# PREPARAÇÃO DOS DADOS
# ==========================================================

def prepare_market_data(data):
    """
    Padroniza os dados de mercado
    para utilização pelos demais módulos.
    """

    if data is None:
        return None

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
        "price": price,
        "history": data,
    }
