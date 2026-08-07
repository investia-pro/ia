"""
===========================================
InvestIA PRO
market.py
Motor de dados do sistema
Versão 0.5.2
===========================================
"""

import streamlit as st
import pandas as pd
import yfinance as yf

from config import (
    DEFAULT_PERIOD,
    DEFAULT_INTERVAL,
    ATIVOS_B3,
    ACOES_USA,
    ETFS,
    FIIS,
    CRIPTOS
)

from indicators import calcular_indicadores
from score import calcular_score


# ==========================================
# Busca de um ativo
# ==========================================

@st.cache_data(ttl=300, show_spinner=False)
def buscar_ativo(ticker):

    try:

        ativo = yf.Ticker(ticker)

        historico = ativo.history(
            period=DEFAULT_PERIOD,
            interval=DEFAULT_INTERVAL
        )

        if historico.empty:
            return None

        indicadores = calcular_indicadores(historico)

        score, recomendacao, motivos = calcular_score(indicadores)

        return {

            "ticker": ticker,

            "historico": historico,

            "indicadores": indicadores,

            "score": score,

            "recomendacao": recomendacao,

            "motivos": motivos

        }

    except Exception:

        return None


# ==========================================
# Scanner
# ==========================================

def scanner(lista):

    resultado = []

    for nome, ticker in lista.items():

        ativo = buscar_ativo(ticker)

        if ativo is None:
            continue

        preco = ativo["indicadores"]["Preço"]

        resultado.append({

            "Ativo": nome,

            "Ticker": ticker,

            "Preço": preco,

            "Score": ativo["score"],

            "Recomendação": ativo["recomendacao"]

        })

    df = pd.DataFrame(resultado)

    if len(df):

        df = df.sort_values(
            by="Score",
            ascending=False
        )

    return df.reset_index(drop=True)


# ==========================================
# Rankings
# ==========================================

def ranking_b3():

    return scanner(ATIVOS_B3)


def ranking_usa():

    return scanner(ACOES_USA)


def ranking_etfs():

    return scanner(ETFS)


def ranking_fiis():

    return scanner(FIIS)


def ranking_crypto():

    return scanner(CRIPTOS)
