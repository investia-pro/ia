"""
InvestIA PRO
Aplicação Principal

Versão: v0.6
Fase: 1.7

Integração da validação completa dos dados.
"""

import streamlit as st

from config import (
    APP_NAME,
    VERSION,
    PAGE_TITLE,
    PAGE_ICON,
    LAYOUT,
)

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
    f"{APP_NAME} • v0.6"
)

st.divider()


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
# DADOS DE MERCADO
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
        "Não foi possível obter os dados do mercado."
    )

    st.exception(error)

    st.stop()


# ==========================================================
# VALIDAÇÃO DOS DADOS DE MERCADO
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
# VALIDAÇÃO COMPLETA
# ==========================================================

validation = validate_complete_analysis(
    market_data=market,
    indicators=indicators,
    minimum_rows=200,
)


# ==========================================================
# TRATAMENTO DE DADOS INVÁLIDOS
# ==========================================================

if not validation["valid"]:

    st.error(
        "⚠️ Os dados disponíveis não são suficientes "
        "para realizar uma análise confiável."
    )

    st.subheader(
        "Diagnóstico dos dados"
    )

    validation_col1, validation_col2 = st.columns(2)


    with validation_col1:

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


    with validation_col2:

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


    # ------------------------------------------------------
    # ERROS DETALHADOS
    # ------------------------------------------------------

    if validation["errors"]:

        st.subheader(
            "Problemas identificados"
        )

        for error_message in validation["errors"]:

            st.write(
                f"• {error_message}"
            )


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
# CABEÇALHO DO ATIVO
# ==========================================================

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

    metric1, metric2 = st.columns(2)


    with metric1:

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


    with metric2:

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

score_percentage = min(
    max(
        float(
            analysis["score"]
        ),
        0,
    ),
    100,
) / 100


st.progress(
    score_percentage
)


# ==========================================================
# INDICADORES TÉCNICOS
# ==========================================================

st.divider()

st.subheader(
    "📐 Indicadores Técnicos"
)


ind1, ind2, ind3, ind4 = st.columns(4)


with ind1:

    st.metric(
        "RSI (14)",
        f"{indicators['rsi']:.2f}",
    )


with ind2:

    st.metric(
        "Média Móvel 21",
        format_currency(
            indicators["ma21"]
        ),
    )


with ind3:

    st.metric(
        "Média Móvel 200",
        format_currency(
            indicators["ma200"]
        ),
    )


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
        market["history"].tail(20),
        use_container_width=True,
    )


# ==========================================================
# STATUS DA ANÁLISE
# ==========================================================

st.divider()

st.success(
    "✅ Análise concluída com dados validados."
)


# ==========================================================
# RODAPÉ
# ==========================================================

st.caption(
    f"{APP_NAME} • v0.6 • Fase 1.7"
)
