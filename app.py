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

from utils import (
    format_currency,
    risk_icon,
)

# ==========================================================
# Configuração da Página
# ==========================================================

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
)

# ==========================================================
# Cabeçalho
# ==========================================================

st.title("📈 InvestIA PRO")

st.caption(f"{APP_NAME} • {VERSION}")

st.divider()

# ==========================================================
# Sidebar
# ==========================================================

st.sidebar.header("Configurações")

asset = st.sidebar.text_input(
    "Ativo",
    value="PETR4"
).upper()

period = st.sidebar.selectbox(
    "Período",
    [
        "6mo",
        "1y",
        "2y",
        "5y"
    ],
    index=1
)

analyze = st.sidebar.button(
    "🔎 Analisar"
)

# ==========================================================
# Tela Inicial
# ==========================================================

if not analyze:

    st.info(
        "Informe um ativo na barra lateral e clique em **Analisar**."
    )

    st.stop()

# ==========================================================
# Busca Mercado
# ==========================================================

try:

    with st.spinner("Buscando dados do mercado..."):

        market = get_market_data(
            asset,
            period
        )

    if market is None:

        st.error(
            "Não foi possível obter dados do ativo."
        )

        st.stop()

except Exception as e:

    st.error(
        "Erro ao consultar o mercado."
    )

    st.exception(e)

    st.stop()

# ==========================================================
# Indicadores
# ==========================================================

try:

    indicators = calculate_indicators(
        market
    )

except Exception as e:

    st.error(
        "Erro ao calcular indicadores."
    )

    st.exception(e)

    st.stop()

# ==========================================================
# Análise
# ==========================================================

try:

    analysis = analyze_asset(
        indicators
    )

except Exception as e:

    st.error(
        "Erro durante a análise."
    )

    st.exception(e)

    st.stop()

# ==========================================================
# Dashboard
# ==========================================================

st.subheader(f"Análise do ativo: {market['asset']}")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Preço",
    format_currency(
        indicators["price"]
    )
)

col2.metric(
    "Score",
    analysis["score"]
)

col3.metric(
    "Tendência",
    analysis["trend"]
)

col4.metric(
    "Recomendação",
    analysis["recommendation"]
)

st.divider()

# ==========================================================
# Indicadores Técnicos
# ==========================================================

st.subheader("Indicadores")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "RSI",
    f"{indicators['rsi']:.2f}"
)

c2.metric(
    "MA21",
    format_currency(
        indicators["ma21"]
    )
)

c3.metric(
    "MA200",
    format_currency(
        indicators["ma200"]
    )
)

c4.metric(
    "Volatilidade",
    f"{indicators['volatility']:.2%}"
)

st.divider()

# ==========================================================
# Análise InvestIA
# ==========================================================

st.subheader("🤖 InvestIA")

st.markdown(
    f"### {risk_icon(analysis['risk'])} Risco: {analysis['risk']}"
)

st.write("### Motivos da recomendação")

for item in analysis["reasons"]:

    st.success(item)

# ==========================================================
# Histórico
# ==========================================================

with st.expander("Visualizar histórico"):

    st.dataframe(
        market["history"].tail(20),
        use_container_width=True
    )

# ==========================================================
# Rodapé
# ==========================================================

st.divider()

st.caption(
    f"{APP_NAME} • {VERSION}"
)
