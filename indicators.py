import pandas as pd


def media_movel(df, periodo):
    return df["Close"].rolling(window=periodo).mean()


def calcular_rsi(df, periodo=14):

    delta = df["Close"].diff()

    ganho = delta.where(delta > 0, 0)

    perda = -delta.where(delta < 0, 0)

    media_ganho = ganho.rolling(periodo).mean()

    media_perda = perda.rolling(periodo).mean()

    rs = media_ganho / media_perda

    rsi = 100 - (100 / (1 + rs))

    return rsi


def calcular_macd(df):

    ema12 = df["Close"].ewm(span=12, adjust=False).mean()

    ema26 = df["Close"].ewm(span=26, adjust=False).mean()

    macd = ema12 - ema26

    sinal = macd.ewm(span=9, adjust=False).mean()

    histograma = macd - sinal

    return macd, sinal, histograma


def bandas_bollinger(df, periodo=20):

    media = df["Close"].rolling(periodo).mean()

    desvio = df["Close"].rolling(periodo).std()

    superior = media + (desvio * 2)

    inferior = media - (desvio * 2)

    return superior, media, inferior


def tendencia(df):

    mm21 = media_movel(df, 21)

    mm72 = media_movel(df, 72)

    mm200 = media_movel(df, 200)

    preco = df["Close"].iloc[-1]

    score = 0

    if preco > mm21.iloc[-1]:
        score += 1

    if preco > mm72.iloc[-1]:
        score += 1

    if preco > mm200.iloc[-1]:
        score += 1

    return score


def volume_medio(df):

    return df["Volume"].rolling(20).mean().iloc[-1]


def calcular_indicadores(df):

    rsi = calcular_rsi(df).iloc[-1]

    macd, sinal, hist = calcular_macd(df)

    bb_sup, bb_med, bb_inf = bandas_bollinger(df)

    return {

        "RSI": round(rsi,2),

        "MACD": round(macd.iloc[-1],4),

        "SINAL": round(sinal.iloc[-1],4),

        "HIST": round(hist.iloc[-1],4),

        "MM9": round(media_movel(df,9).iloc[-1],2),

        "MM21": round(media_movel(df,21).iloc[-1],2),

        "MM72": round(media_movel(df,72).iloc[-1],2),

        "MM200": round(media_movel(df,200).iloc[-1],2),

        "BB_SUP": round(bb_sup.iloc[-1],2),

        "BB_MED": round(bb_med.iloc[-1],2),

        "BB_INF": round(bb_inf.iloc[-1],2),

        "TENDENCIA": tendencia(df),

        "VOLUME_MEDIO": round(volume_medio(df),0)

    }
