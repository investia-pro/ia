import streamlit as st

from market import (
    buscar_ativo,
    ranking_b3,
    ranking_usa,
    ranking_crypto
)

from charts import (
    grafico_medias,
    grafico_volume
)

st.set_page_config(
    page_title="InvestIA PRO",
    page_icon="📈",
    layout="wide"
)

# =====================================
# Cabeçalho
# =====================================

st.title("📈 InvestIA PRO")

st.caption("Scanner Inteligente de Investimentos")

if st.button("🔄 Atualizar"):
    st.rerun()

st.divider()

# =====================================
# Pesquisa
# =====================================

ativo = st.text_input(
    "Pesquisar ativo",
    placeholder="PETR4, VALE3, AAPL, BTC-USD..."
)

if ativo:

    ticker = ativo.upper()

    if ticker in ["PETR4", "VALE3", "ITUB4", "BBAS3", "BBDC4", "ABEV3", "WEGE3", "RENT3", "PRIO3", "SUZB3"]:
        ticker += ".SA"

    ativo_dados = buscar_ativo(ticker)

    if ativo_dados:

        st.header(f"Análise - {ticker}")

        historico = ativo_dados["historico"]

        indicadores = ativo_dados["indicadores"]

        score = ativo_dados["score"]

        recomendacao = ativo_dados["recomendacao"]

        motivos = ativo_dados["motivos"]

        preco = historico["Close"].iloc[-1]

        anterior = historico["Close"].iloc[-2]

        variacao = ((preco - anterior) / anterior) * 100

        moeda = "R$" if ticker.endswith(".SA") else "US$"

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Preço",
            f"{moeda} {preco:,.2f}",
            f"{variacao:.2f}%"
        )

        c2.metric(
            "Score",
            score
        )

        c3.metric(
            "Recomendação",
            recomendacao
        )

        st.progress(score / 100)

        st.subheader("Motivos")

        for motivo in motivos:

            st.write(f"✅ {motivo}")

        st.divider()

        st.subheader("Gráfico")

        st.plotly_chart(
            grafico_medias(
                historico,
                ticker
            ),
            use_container_width=True
        )

        st.plotly_chart(
            grafico_volume(
                historico
            ),
            use_container_width=True
        )

        st.divider()

        st.subheader("Indicadores")

        st.dataframe(indicadores)

else:

    st.info("Pesquise um ativo para iniciar a análise.")

st.divider()

# =====================================
# Scanner
# =====================================

aba1, aba2, aba3 = st.tabs(
    [
        "🇧🇷 B3",
        "🇺🇸 EUA",
        "₿ Criptos"
    ]
)

with aba1:

    st.subheader("Ranking B3")

    st.dataframe(
        ranking_b3(),
        use_container_width=True
    )

with aba2:

    st.subheader("Ranking EUA")

    st.dataframe(
        ranking_usa(),
        use_container_width=True
    )

with aba3:

    st.subheader("Ranking Criptomoedas")

    st.dataframe(
        ranking_crypto(),
        use_container_width=True
    )
