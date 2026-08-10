"""
InvestIA PRO
Aplicação Principal

Versão: v0.5.3 Stable
"""

import streamlit as st

from config import (
    APP_NAME,
    VERSION,
    PAGE_TITLE,
    PAGE_ICON,
    LAYOUT,
    DEFAULT_PERIOD,
)

from market import get_market_data
from indicators import calculate_indicators
from analysis import analyze_asset
from charts import create_price_chart

from utils import (
    format_currency,
    risk_icon,
)


# ==========================================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================================

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
)


# ==========================================================
# CABEÇALHO
# ==========================================================

st.title("📈 InvestIA PRO")

st.caption(
    f"{APP_NAME} • {VERSION}"
)

st.divider()


# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.header("Configurações")


asset = st.sidebar.text_input(
    "Ativo",
    value="PETR4",
).strip().upper()


period = st.sidebar.selectbox(
    "Período",
    [
        "6mo",
        "1y",
        "2y",
        "5y",
    ],
    index=1,
)


analyze = st.sidebar.button(
    "🔎 Analisar",
    use_container_width=True,
)


# ==========================================================
# TELA INICIAL
# ==========================================================

if not analyze:

    st.info(
        "Informe um ativo e clique em **Analisar**."
    )

    st.stop()


# ==========================================================
# VALIDAÇÃO DO ATIVO
# ==========================================================

if not asset:

    st.warning(
        "Digite o código de um ativo."
    )

    st.stop()


# ==========================================================
# BUSCA DOS DADOS DE MERCADO
# ==========================================================

try:

    with st.spinner(
        "Buscando dados do mercado..."
    ):

        market = get_market_data(
            asset,
            period,
        )

except Exception as error:

    st.error(
        "Não foi possível obter os dados do ativo."
    )

    st.exception(error)

    st.stop()


if market is None:

    st.error(
        "Não foi possível obter dados do ativo."
    )

    st.stop()


# ==========================================================
# INDICADORES
# ==========================================================

try:

    indicators = calculate_indicators(
        market
    )

except Exception as error:

    st.error(
        "Erro ao calcular os indicadores técnicos."
    )

    st.exception(error)

    st.stop()


# ==========================================================
# ANÁLISE
# ==========================================================

try:

    analysis = analyze_asset(
        indicators
    )

except Exception as error:

    st.error(
        "Erro durante a análise do ativo."
    )

    st.exception(error)

    st.stop()


# ==========================================================
# DASHBOARD PRINCIPAL
# ==========================================================

st.subheader(
    f"📊 Análise do ativo: {market['asset']}"
)


col1, col2, col3, col4 = st.columns(4)


# ----------------------------------------------------------
# PREÇO
# ----------------------------------------------------------

with col1:

    st.metric(
        "Preço atual",
        format_currency(
            indicators["price"]
        ),
    )


# ----------------------------------------------------------
# SCORE
# ----------------------------------------------------------

with col2:

    st.metric(
        "Score InvestIA",
        analysis["score"],
    )


# ----------------------------------------------------------
# TENDÊNCIA
# ----------------------------------------------------------

with col3:

    st.metric(
        "Tendência",
        analysis["trend"],
    )


# ----------------------------------------------------------
# RECOMENDAÇÃO
# ----------------------------------------------------------

with col4:

    st.metric(
        "Recomendação",
        analysis["recommendation"],
    )


# ==========================================================
# INDICADORES TÉCNICOS
# ==========================================================

st.divider()

st.subheader(
    "📐 Indicadores Técnicos"
)


ind1, ind2, ind3, ind4 = st.columns(4)


# ----------------------------------------------------------
# RSI
# ----------------------------------------------------------

with ind1:

    st.metric(
        "RSI (14)",
        f"{indicators['rsi']:.2f}",
    )


# ----------------------------------------------------------
# MA21
# ----------------------------------------------------------

with ind2:

    st.metric(
        "Média Móvel 21",
        format_currency(
            indicators["ma21"]
        ),
    )


# ----------------------------------------------------------
# MA200
# ----------------------------------------------------------

with ind3:

    st.metric(
        "Média Móvel 200",
        format_currency(
            indicators["ma200"]
        ),
    )


# ----------------------------------------------------------
# VOLATILIDADE
# ----------------------------------------------------------

with ind4:

    st.metric(
        "Volatilidade",
        f"{indicators['volatility']:.2%}",
    )


# ==========================================================
# GRÁFICO
# ==========================================================

st.divider()

st.subheader(
    "📈 Evolução do Ativo"
)


try:

    fig = create_price_chart(
        market["history"],
        indicators,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

except Exception as error:

    st.error(
        "Não foi possível gerar o gráfico."
    )

    st.exception(error)


# ==========================================================
# ANÁLISE INVESTIA
# ==========================================================

st.divider()

st.subheader(
    "🤖 Análise InvestIA"
)


# ----------------------------------------------------------
# RISCO
# ----------------------------------------------------------

risk = analysis.get(
    "risk",
    "N/A",
)


st.markdown(
    f"### {risk_icon(risk)} Risco: {risk}"
)


# ----------------------------------------------------------
# SCORE
# ----------------------------------------------------------

st.write(
    f"**Score InvestIA:** {analysis['score']}"
)


# ----------------------------------------------------------
# FUNDAMENTAÇÃO
# ----------------------------------------------------------

st.write(
    "### Fundamentação da análise"
)


reasons = analysis.get(
    "reasons",
    [],
)


if reasons:

    for reason in reasons:

        st.write(
            f"✔️ {reason}"
        )

else:

    st.info(
        "Não foram encontradas justificativas "
        "adicionais para esta análise."
    )


# ==========================================================
# HISTÓRICO
# ==========================================================

st.divider()

with st.expander(
    "📋 Visualizar histórico do ativo"
):

    st.dataframe(
        market["history"].tail(20),
        use_container_width=True,
    )


# ==========================================================
# RODAPÉ
# ==========================================================

st.divider()

st.caption(
    f"{APP_NAME} • {VERSION}"
)
