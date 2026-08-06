import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="InvestIA PRO",
    page_icon="📈",
    layout="wide"
)

st.title("📈 InvestIA PRO")

st.button("🔄 Atualizar")

st.divider()

ativo_digitado = st.text_input(
    "🔍 Pesquisar ativo",
    placeholder="Ex: PETR4, VALE3, AAPL, BTC-USD"
)

ativos = {
    "PETR4": "PETR4.SA",
    "VALE3": "VALE3.SA",
    "ITUB4": "ITUB4.SA",
    "AAPL": "AAPL",
    "NVDA": "NVDA",
    "BTC": "BTC-USD",
    "ETH": "ETH-USD"
}

if ativo_digitado:

    ticker = ativo_digitado.upper()

    if ticker in ["PETR4","VALE3","ITUB4"]:
        ticker += ".SA"

    try:

        dados = yf.Ticker(ticker)
        hist = dados.history(period="2d")

        atual = hist["Close"].iloc[-1]
        anterior = hist["Close"].iloc[-2]

        variacao = ((atual-anterior)/anterior)*100

        moeda = "R$" if ticker.endswith(".SA") else "US$"

        st.metric(
            ticker.replace(".SA",""),
            f"{moeda} {atual:,.2f}",
            f"{variacao:.2f}%"
        )

    except:
        st.error("Ativo não encontrado.")

st.divider()

st.subheader("Mercado Hoje")

col1,col2,col3 = st.columns(3)

lista = list(ativos.items())

for i,(nome,ticker) in enumerate(lista):

    try:

        dados = yf.Ticker(ticker)

        hist = dados.history(period="2d")

        atual = hist["Close"].iloc[-1]
        anterior = hist["Close"].iloc[-2]

        variacao=((atual-anterior)/anterior)*100

        moeda="R$" if ticker.endswith(".SA") else "US$"

        if i%3==0:
            coluna=col1
        elif i%3==1:
            coluna=col2
        else:
            coluna=col3

        coluna.metric(
            nome,
            f"{moeda} {atual:,.2f}",
            f"{variacao:.2f}%"
        )

    except:

        pass
