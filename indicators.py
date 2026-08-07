"""
===========================================
InvestIA PRO
indicators.py
Indicadores Técnicos
===========================================
"""

import pandas as pd


def calcular_rsi(df, periodo=14):
    delta = df["Close"].diff()

    ganho = delta.where(delta > 0, 0).rolling(periodo).mean()
    perda = (-delta.where(delta < 0, 0)).rolling(periodo).mean()

    rs = ganho / perda

    rsi = 100 - (100 / (1 + rs))

    return rsi


def calcular_medias(df):

    df["MM9"] = df["Close"].rolling(9).mean()

    df["MM21"] = df["Close"].rolling(21).mean()

    df["MM72"] = df["Close"].rolling(72).mean()

    df["MM200"] = df["Close"].rolling(200).mean()

    return df


def calcular_macd(df):

    ema12 = df["Close"].ewm(span=12, adjust=False).mean()

    ema26 = df["Close"].ewm(span=26, adjust=False).mean()

    macd = ema12 - ema26

    sinal = macd.ewm(span=9, adjust=False).mean()

    histograma = macd - sinal

    return macd, sinal, histograma


def calcular_bollinger(df, periodo=20):

    media = df["Close"].rolling(periodo).mean()

    desvio = df["Close"].rolling(periodo).std()

    superior = media + (desvio * 2)

    inferior = media - (desvio * 2)

    return superior, media, inferior


def calcular_indicadores(df):

    df = df.copy()

    df = calcular_medias(df)

    df["RSI"] = calcular_rsi(df)

    macd, sinal, hist = calcular_macd(df)

    df["MACD"] = macd

    df["MACD_SINAL"] = sinal

    df["MACD_HIST"] = hist

    sup, med, inf = calcular_bollinger(df)

    df["BB_SUP"] = sup

    df["BB_MED"] = med

    df["BB_INF"] = inf

    ultimo = df.iloc[-1]

    indicadores = {

        "Preço": round(ultimo["Close"], 2),

        "RSI": round(ultimo["RSI"], 2),

        "MM9": round(ultimo["MM9"], 2),

        "MM21": round(ultimo["MM21"], 2),

        "MM72": round(ultimo["MM72"], 2),

        "MM200": round(ultimo["MM200"], 2),

        "MACD": round(ultimo["MACD"], 4),

        "MACD_SINAL": round(ultimo["MACD_SINAL"], 4),

        "BB_SUP": round(ultimo["BB_SUP"], 2),

        "BB_MED": round(ultimo["BB_MED"], 2),

        "BB_INF": round(ultimo["BB_INF"], 2)

    }

    return indicadores
