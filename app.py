import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="InvestIA PRO",
    page_icon="📈",
    layout="wide"
)

st.title("📈 InvestIA PRO")

ativos = {
    "PETR4": "PETR4.SA",
    "VALE3": "VALE3.SA",
    "ITUB4": "ITUB4.SA",
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "AAPL": "AAPL",
    "NVDA": "NVDA"
}

st.subheader("Mercado em tempo real")

for nome, ticker in ativos.items():
    try:
        ativo = yf.Ticker(ticker)
        preco = ativo.history(period="1d")["Close"].iloc[-1]
if ticker.endswith(".SA"):
    valor = f"R$ {preco:,.2f}"
else:
    valor = f"US$ {preco:,.2f}"

st.metric(nome, valor)
    except:
        st.metric(nome, "Indisponível")
