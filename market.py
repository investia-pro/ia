"""
InvestIA PRO
Módulo de dados de mercado

Versão: v0.5.3
"""

import yfinance as yf
import streamlit as st
import pandas as pd



# =====================================
# Busca dados históricos
# =====================================

@st.cache_data(
    ttl=300
)
def get_market_data(
        asset,
        period="1y"
):

    """
    Busca dados históricos do ativo.

    Retorna DataFrame com:
    Open
    High
    Low
    Close
    Volume
    """

    try:


        ticker = yf.Ticker(

            f"{asset}.SA"

        )


        data = ticker.history(

            period=period

        )



        # -----------------------------
        # Validação
        # -----------------------------


        if data.empty:

            return None



        # Remove linhas sem preço

        data = data.dropna()



        return data



    except Exception:


        return None




# =====================================
# Último preço
# =====================================

def get_current_price(data):

    """
    Retorna último preço negociado.
    """

    try:


        price = data["Close"].iloc[-1]


        return float(price)



    except Exception:


        return None




# =====================================
# Preparação dos dados
# =====================================

def prepare_market_data(data):

    """
    Padroniza dados para análise.
    """

    if data is None or data.empty:

        return None



    result = {

        "price":
            float(
                data["Close"].iloc[-1]
            ),


        "history":
            data

    }



    return result
