import pandas as pd
import yfinance as yf
from score import calcular_score

ATIVOS = {
    "PETR4": "PETR4.SA",
    "VALE3": "VALE3.SA",
    "ITUB4": "ITUB4.SA",
    "AAPL": "AAPL",
    "NVDA": "NVDA",
    "BTC": "BTC-USD",
    "ETH": "ETH-USD"
}


def obter_ranking():

    lista = []

    for nome, ticker in ATIVOS.items():

        try:

            dados = yf.Ticker(ticker)

            hist = dados.history(period="2d")

            if len(hist) < 2:
                continue

            atual = hist["Close"].iloc[-1]
            anterior = hist["Close"].iloc[-2]

            variacao = ((atual - anterior) / anterior) * 100

            score, recomendacao = calcular_score(variacao)

            lista.append({
                "Ativo": nome,
                "Preço": round(atual, 2),
                "Variação (%)": round(variacao, 2),
                "Score": score,
                "Recomendação": recomendacao
            })

        except:
            pass

    df = pd.DataFrame(lista)

    if len(df):

        df = df.sort_values(
            by="Score",
            ascending=False
        )

    return df
