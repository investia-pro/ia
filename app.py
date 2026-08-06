import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

from score import calcular_score

st.set_page_config(
    page_title="InvestIA PRO",
    page_icon="📈",
    layout="wide"
)

# --------------------------
# Funções
# --------------------------

def obter_ticker(codigo):
    codigo = codigo.upper()

    if codigo in ["PETR4", "VALE3", "ITUB4"]:
        return codigo + ".SA"

    return codigo


def obter_moeda(ticker):
    if ticker.endswith(".SA"):
        return "R$"
    return "US$"


def exibir_ativo(nome, ticker):

    try:

        dados = yf.Ticker(ticker)

        hist_curto = dados.history(period="2d")

        if len(hist_curto) < 2:
            st.warning(f"Sem dados para {nome}")
            return

        atual = hist_curto["Close"].iloc[-1]
        anterior = hist_curto["Close"].iloc[-2]

        variacao = ((atual - anterior) / anterior) * 100

        score, recomendacao = calcular_score(variacao)

        moeda = obter_moeda(ticker)

        st.metric(
            nome,
            f"{moeda} {atual:,.2f}",
            f"{variacao:.2f}%"
        )

        st.progress(score / 100)

        st.write(f"**Score:** {score}/100")

        st.write(recomendacao)

        st.divider()

        st.subheader("Gráfico (6 meses)")

        hist = dados.history(period="6mo")

        fig = go.Figure()

        fig.add_trace(
            go.Candlestick(
                x=hist.index,
                open=hist["Open"],
                high=hist["High"],
                low=hist["Low"],
                close=hist["Close"],
                name=nome
            )
        )

        fig.update_layout(
            height=450,
            xaxis_rangeslider_visible=False,
            margin=dict(l=5, r=5, t=25, b=5)
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        info = dados.info

        st.subheader("Resumo")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Máxima do dia",
                f"{moeda} {info.get('dayHigh','-')}"
            )

        with c2:
            st.metric(
                "Mínima do dia",
                f"{moeda} {info.get('dayLow','-')}"
            )

        with c3:
            volume = info.get("volume", "-")
            st.metric(
                "Volume",
                volume
            )

    except Exception as erro:

        st.error(f"Erro ao consultar {nome}")
        st.write(erro)


# --------------------------
# Interface
# --------------------------

st.title("📈 InvestIA PRO")

if st.button("🔄 Atualizar"):
    st.rerun()

st.divider()

ativo = st.text_input(
    "Pesquisar ativo",
    placeholder="PETR4, VALE3, AAPL, NVDA, BTC-USD..."
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

# --------------------------
# Pesquisa
# --------------------------

if ativo:

    ticker = obter_ticker(ativo)

    st.header("Resultado da Pesquisa")

    exibir_ativo(
        ativo.upper(),
        ticker
    )

st.divider()

# --------------------------
# Mercado
# --------------------------

st.header("Mercado Hoje")

col1, col2, col3 = st.columns(3)

lista = list(ativos.items())

for indice, (nome, ticker) in enumerate(lista):

    if indice % 3 == 0:
        with col1:
            exibir_ativo(nome, ticker)

    elif indice % 3 == 1:
        with col2:
            exibir_ativo(nome, ticker)

    else:
        with col3:
            exibir_ativo(nome, ticker)
