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

def buscar_ativo(ticker):

    dados = yf.Ticker(ticker)

    df = dados.history(period=DEFAULT_PERIOD)

    if df.empty:
        return None

    indicadores = calcular_indicadores(df)

    score, recomendacao, motivos = calcular_score(indicadores)

    return {

        "ticker": ticker,

        "dados": dados,

        "historico": df,

        "indicadores": indicadores,

        "score": score,

        "recomendacao": recomendacao,

        "motivos": motivos

    }


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
