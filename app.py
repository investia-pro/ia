"""
InvestIA PRO
Aplicação Principal

Versão: v0.6
Fase: 1.7 - Validação e Qualidade dos Dados
"""

import streamlit as st

from market import get_market_data
from indicators import calculate_indicators
from analysis import analyze_asset
from charts import create_price_chart

from utils import (
    format_currency,
    risk_icon,
    validate_complete_analysis,
)


# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

APP_NAME = "InvestIA PRO"
VERSION = "v0.6"

st.set_page_config(
    page_title=APP_NAME,
    page_icon="📈",
    layout="wide",
)


# ==========================================================
# CABEÇALHO
# ==========================================================

st.title("📈 InvestIA PRO")

st.caption(
    f"{APP_NAME} • {VERSION}"
)


# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.header(
    "Configurações"
)


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


analyze_button = st.sidebar.button(
    "🔎 Analisar",
    use_container_width=True,
)


# ==========================================================
# TELA INICIAL
# ==========================================================

if not analyze_button:

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
        "Erro ao buscar os dados do mercado."
    )

    st.exception(error)

    st.stop()


# ==========================================================
# VALIDAÇÃO DO RETORNO DO MARKET.PY
# ==========================================================

if market is None:

    st.error(
        f"Não foram encontrados dados para o ativo "
        f"**{asset}**."
    )

    st.info(
        "Verifique o código do ativo e tente novamente."
    )

    st.stop()


# ==========================================================
# NORMALIZAÇÃO DOS DADOS
# ==========================================================

"""
O market.py normalmente retorna:

{
    "price": ...,
    "history": DataFrame
}

O indicators.py espera esse objeto completo.

Por isso NÃO enviamos somente o DataFrame
para calculate_indicators().
"""


if isinstance(market, dict):

    history = market.get(
        "history"
    )

    market_for_indicators = market

else:

    history = market

    market_for_indicators = {
        "history": market
    }


# ==========================================================
# VALIDAÇÃO DO HISTÓRICO
# ==========================================================

if history is None:

    st.error(
        "O histórico do ativo não está disponível."
    )

    st.stop()


try:

    if history.empty:

        st.error(
            "O histórico retornado está vazio."
        )

        st.stop()

except AttributeError:

    st.error(
        "Formato de histórico inválido."
    )

    st.stop()


# ==========================================================
# CÁLCULO DOS INDICADORES
# ==========================================================

try:

    indicators = calculate_indicators(
        market_for_indicators
    )

except Exception as error:

    st.error(
        "Erro ao calcular os indicadores técnicos."
    )

    st.exception(error)

    st.stop()


# ==========================================================
# VALIDAÇÃO COMPLETA
# ==========================================================

validation = validate_complete_analysis(
    market_data=history,
    indicators=indicators,
    minimum_rows=200,
)


# ==========================================================
# DIAGNÓSTICO DE DADOS
# ==========================================================

if not validation["valid"]:

    st.error(
        "⚠️ Os dados disponíveis não são suficientes "
        "para realizar uma análise confiável."
    )

    st.subheader(
        "Diagnóstico dos dados"
    )

    col1, col2 = st.columns(2)


    # ======================================================
    # MERCADO
    # ======================================================

    with col1:

        st.write(
            "### Mercado"
        )

        if validation["market_data"]:

            st.success(
                "✓ Dados de mercado encontrados."
            )

        else:

            st.error(
                "✗ Dados de mercado indisponíveis."
            )


        st.write(
            "### Histórico"
        )

        if validation["history"]:

            st.success(
                "✓ Histórico suficiente."
            )

        else:

            st.warning(
                "⚠ Histórico insuficiente."
            )


    # ======================================================
    # ESTRUTURA
    # ======================================================

    with col2:

        st.write(
            "### Estrutura"
        )

        if validation["columns"]:

            st.success(
                "✓ Estrutura de mercado válida."
            )

        else:

            st.error(
                "✗ Colunas necessárias ausentes."
            )


        st.write(
            "### Indicadores"
        )

        if validation["indicators"]:

            st.success(
                "✓ Indicadores válidos."
            )

        else:

            st.error(
                "✗ Indicadores inválidos ou incompletos."
            )


    # ======================================================
    # PROBLEMAS IDENTIFICADOS
    # ======================================================

    if validation["errors"]:

        st.subheader(
            "Problemas identificados"
        )

        for message in validation["errors"]:

            st.write(
                f"• {message}"
            )


    st.stop()


# ==========================================================
# ANÁLISE DO ATIVO
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
# TÍTULO
# ==========================================================

st.divider()

st.subheader(
    f"📊 Análise do ativo: {asset}"
)


# ==========================================================
# RESUMO PRINCIPAL
# ==========================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Preço atual",
        format_currency(
            indicators["price"]
        ),
    )


with col2:

    st.metric(
        "Score InvestIA",
        f"{analysis['score']:.0f}/100",
    )


with col3:

    st.metric(
        "Tendência",
        analysis["trend"],
    )


with col4:

    st.metric(
        "Recomendação",
        analysis["recommendation"],
    )


# ==========================================================
# SCORE INVESTIA 2.0
# ==========================================================

st.divider()

st.subheader(
    "🤖 InvestIA Score 2.0"
)


score_col1, score_col2 = st.columns(
    [1, 2]
)


# ==========================================================
# SCORE PRINCIPAL
# ==========================================================

with score_col1:

    st.metric(
        "Score",
        f"{analysis['score']:.0f}/100",
    )

    st.write(
        f"**Classificação:** "
        f"{analysis.get('classification', 'N/A')}"
    )

    st.write(
        f"**Sinal:** "
        f"{analysis.get('signal', 'N/A')}"
    )


# ==========================================================
# COMPOSIÇÃO DO SCORE
# ==========================================================

with score_col2:

    st.write(
        "### Composição do Score"
    )

    metric_col1, metric_col2 = st.columns(2)


    with metric_col1:

        st.metric(
            "RSI",
            f"{analysis['rsi_score']:.0f}/100",
        )

        st.metric(
            "MA21",
            f"{analysis['ma21_score']:.0f}/100",
        )

        st.metric(
            "MA200",
            f"{analysis['ma200_score']:.0f}/100",
        )


    with metric_col2:

        st.metric(
            "Tendência",
            f"{analysis['trend_score']:.0f}/100",
        )

        st.metric(
            "Risco",
            f"{analysis['risk_score']:.0f}/100",
        )

        st.metric(
            "Técnico",
            f"{analysis['technical_score']:.0f}/100",
        )


# ==========================================================
# BARRA DO SCORE
# ==========================================================

score_value = float(
    analysis["score"]
)

score_value = max(
    0,
    min(
        100,
        score_value,
    ),
)


st.progress(
    score_value / 100
)


# ==========================================================
# INDICADORES TÉCNICOS
# ==========================================================

st.divider()

st.subheader(
    "📐 Indicadores Técnicos"
)


ind_col1, ind_col2, ind_col3, ind_col4 = st.columns(4)


with ind_col1:

    st.metric(
        "RSI (14)",
        f"{indicators['rsi']:.2f}",
    )


with ind_col2:

    st.metric(
        "Média Móvel 21",
        format_currency(
            indicators["ma21"]
        ),
    )


with ind_col3:

    st.metric(
        "Média Móvel 200",
        format_currency(
            indicators["ma200"]
        ),
    )


with ind_col4:

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
        history
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

except Exception as error:

    st.warning(
        "Não foi possível gerar o gráfico."
    )

    st.exception(error)


# ==========================================================
# FUNDAMENTAÇÃO
# ==========================================================

st.divider()

st.subheader(
    "🧠 Fundamentação da análise"
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
# GESTÃO DE RISCO
# ==========================================================

st.divider()

st.subheader(
    "⚠️ Gestão de risco"
)


risk = analysis.get(
    "risk",
    "N/A",
)


st.markdown(
    f"### {risk_icon(risk)} {risk}"
)


st.write(
    f"Score de controle de risco: "
    f"**{analysis['risk_score']:.0f}/100**"
)


st.caption(
    "Quanto maior o Score de risco, melhor o controle "
    "da volatilidade observada."
)


# ==========================================================
# HISTÓRICO
# ==========================================================

st.divider()

with st.expander(
    "📋 Visualizar histórico do ativo"
):

    st.dataframe(
        history.tail(20),
        use_container_width=True,
    )


# ==========================================================
# STATUS FINAL
# ==========================================================

st.divider()

st.success(
    "✅ Análise concluída com dados validados."
)


# ==========================================================
# RODAPÉ
# ==========================================================

st.caption(
    f"{APP_NAME} • {VERSION} • Fase 1.7"
)
