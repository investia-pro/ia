import streamlit as st
import yfinance as yf
from score import calcular_score

st.set_page_config(
    page_title="InvestIA PRO",
    page_icon="📈",
    layout="wide"
)

st.title("📈 InvestIA PRO")

if st.button("🔄 Atualizar"):
    st.rerun()

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


def exibir_ativo(nome, ticker):

    try:

        dados = yf.Ticker(ticker)
        hist = dados.history(period="2d")

        if len(hist) < 2:
            st.warning(f"Sem dados para {nome}")
            return

        atual = hist["Close"].iloc[-1]
        anterior = hist["Close"].iloc[-2]

        variacao = ((atual - anterior) / anterior) * 100

        score, recomendacao = calcular_score(variacao)

        moeda = "R$" if ticker.endswith(".SA") else "US$"

        st.metric(
            nome,
            f"{moeda} {atual:,.2f}",
            f"{variacao:.2f}%"
        )

        st.progress(score / 100)

        st.write(f"**Score:** {score}/100")

        st.write(recomendacao)

    except Exception as e:
        st.error(f"Erro ao consultar {nome}")


# ---------------------------
# Pesquisa
# ---------------------------

if ativo_digitado:

    ticker = ativo_digitado.upper()

    if ticker in ["PETR4", "VALE3", "ITUB4"]:
        ticker += ".SA"

    st.subheader("Resultado da Pesquisa")

    exibir_ativo(
        ticker.replace(".SA", ""),
        ticker
    )

st.divider()

st.subheader("Mercado Hoje")

col1, col2, col3 = st.columns(3)

lista = list(ativos.items())

for i, (nome, ticker) in enumerate(lista):

    if i % 3 == 0:
        with col1:
            exibir_ativo(nome, ticker)

    elif i % 3 == 1:
        with col2:
            exibir_ativo(nome, ticker)

    else:
        with col3:
            exibir_ativo(nome, ticker)
