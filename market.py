import streamlit as st
import yfinance as yf
import pandas as pd
import yfinance as yf
import pandas as pd

from config import (
    ATIVOS_B3,
    ACOES_USA,
    CRIPTOS,
    DEFAULT_PERIOD
)

from indicators import calcular_indicadores
from score import calcular_score


# ==========================================
# Busca um ativo
# ==========================================

@st.cache_data(ttl=300, show_spinner=False)
def buscar_ativo(ticker):

    @st.cache_data(ttl=300, show_spinner=False)
def buscar_varios_ativos(lista_tickers):

    resultado = {}

    for ticker in lista_tickers:

        try:

            dados = buscar_ativo(ticker)

            if dados:

                resultado[ticker] = dados

        except Exception:

            pass

    return resultado
# ==========================================
# Scanner
# ==========================================

def scanner(lista):

    resultado = []

    for nome, ticker in lista.items():

        try:

            ativo = buscar_ativo(ticker)

            if ativo is None:
                continue

            ultimo = ativo["historico"]["Close"].iloc[-1]

            anterior = ativo["historico"]["Close"].iloc[-2]

            variacao = ((ultimo - anterior) / anterior) * 100

            resultado.append({

                "Ativo": nome,

                "Ticker": ticker,

                "Preço": round(ultimo, 2),

                "Variação": round(variacao, 2),

                "Score": ativo["score"],

                "Recomendação": ativo["recomendacao"]

            })

        except Exception:

            continue

    df = pd.DataFrame(resultado)

    if len(df):

        df = df.sort_values(
            by="Score",
            ascending=False
        )

    return df


# ==========================================
# Rankings
# ==========================================

def ranking_b3():

    return scanner(ATIVOS_B3)


def ranking_usa():

    return scanner(ACOES_USA)


def ranking_crypto():

    return scanner(CRIPTOS)
