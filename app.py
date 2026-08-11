"""
InvestIA PRO
Aplicação principal

Versão: v0.6
Fase: 2.3 - Integração do Score 2.0
"""

import streamlit as st

from market import get_market_data
from indicators import calculate_indicators
from analysis import analyze_asset
from charts import create_price_chart

from utils import (
    validate_market_data,
    validate_analysis_data,
    format_currency,
    risk_icon,
)


# ==========================================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================================

st.set_page_config(
    page_title="InvestIA PRO",
    page_icon="📈",
    layout="wide",
)


# ==========================================================
# CABEÇALHO
# ==========================================================

st.title("📈 InvestIA PRO")

st.caption(
    "Análise inteligente de ativos financeiros"
)


# ==========================================================
# ENTRADA DO USUÁRIO
# ==========================================================

col_input, col_period = st.columns(
    [2, 1]
)


with col_input:

    asset = st.text_input(
        "Digite o código do ativo",
        value="PETR4",
        max_chars=10,
    )


with col_period:

    period = st.selectbox(
        "Período de análise",
        [
            "6mo",
            "1y",
            "2y",
            "5y",
        ],
        index=1,
    )


analyze_button = st.button(
    "🔎 Analisar ativo",
    use_container_width=True,
)


# ==========================================================
# FUNÇÃO DE EXIBIÇÃO DE SCORE
# ==========================================================

def display_score_component(
    label,
    value,
):
    """
    Exibe um componente individual do Score.
    """

    try:

        value = float(value)

    except (TypeError, ValueError):

        value = 0

    st.metric(
        label,
        f"{value:.0f}/100",
    )


# ==========================================================
# EXECUÇÃO PRINCIPAL
# ==========================================================

if analyze_button:

    # ------------------------------------------------------
    # Validação do ativo
    # ------------------------------------------------------

    asset = asset.strip().upper()

    if not asset:

        st.warning(
            "Digite o código de um ativo."
        )

        st.stop()


    try:

        # ==================================================
        # BUSCA DE DADOS
        # ==================================================

        with st.spinner(
            "Buscando dados do mercado..."
        ):

            market_data = get_market_data(
                asset,
                period,
            )


        # ==================================================
        # VALIDAÇÃO DO MERCADO
        # ==================================================

        if not validate_market_data(
            market_data
        ):

            st.error(
                f"Não foi possível obter dados para {asset}."
            )

            st.info(
                "Verifique o código do ativo e tente novamente."
            )

            st.stop()


        # ==================================================
        # INDICADORES
        # ==================================================

        with st.spinner(
            "Calculando indicadores..."
        ):

            indicators = calculate_indicators(
                market_data
            )


        # ==================================================
        # PREPARAÇÃO DOS DADOS
        # ==================================================

        analysis_data = {
            **indicators
        }


        # ==================================================
        # VALIDAÇÃO DA ANÁLISE
        # ==================================================

        if not validate_analysis_data(
            analysis_data
        ):

            st.warning(
                "Não existem dados suficientes "
                "para realizar a análise."
            )

            st.stop()


        # ==================================================
        # MOTOR DE ANÁLISE
        # ==================================================

        with st.spinner(
            "Executando análise InvestIA..."
        ):

            result = analyze_asset(
                analysis_data
            )


        # ==================================================
        # CABEÇALHO DO ATIVO
        # ==================================================

        st.divider()

        st.subheader(
            f"📊 Análise: {asset}"
        )


        # ==================================================
        # CARDS PRINCIPAIS
        # ==================================================

        col1, col2, col3, col4 = st.columns(
            4
        )


        with col1:

            st.metric(
                "Preço atual",
                format_currency(
                    analysis_data["price"]
                ),
            )


        with col2:

            st.metric(
                "Score InvestIA",
                f'{result["score"]:.0f}/100',
            )


        with col3:

            st.metric(
                "Tendência",
                result["trend"],
            )


        with col4:

            st.metric(
                "Recomendação",
                result["recommendation"],
            )


        # ==================================================
        # STATUS DA ANÁLISE
        # ==================================================

        st.divider()

        col1, col2, col3 = st.columns(
            3
        )


        with col1:

            st.write(
                "**Classificação**"
            )

            st.write(
                result["classification"]
            )


        with col2:

            st.write(
                "**Sinal**"
            )

            st.write(
                result["signal"]
            )


        with col3:

            st.write(
                "**Risco**"
            )

            st.write(
                f'{risk_icon(result["risk"])} '
                f'{result["risk"]}'
            )


        # ==================================================
        # SCORE DETALHADO
        # ==================================================

        st.divider()

        st.subheader(
            "🎯 Componentes do Score"
        )


        col1, col2, col3 = st.columns(
            3
        )


        with col1:

            display_score_component(
                "RSI",
                result["rsi_score"],
            )

            display_score_component(
                "MA21",
                result["ma21_score"],
            )


        with col2:

            display_score_component(
                "MA200",
                result["ma200_score"],
            )

            display_score_component(
                "Tendência",
                result["trend_score"],
            )


        with col3:

            display_score_component(
                "Risco",
                result["risk_score"],
            )

            display_score_component(
                "Técnico",
                result["technical_score"],
            )


        # ==================================================
        # GRÁFICO
        # ==================================================

        st.divider()

        st.subheader(
            "📈 Evolução do preço"
        )


        fig = create_price_chart(
            market_data
        )


        st.plotly_chart(
            fig,
            use_container_width=True,
        )


        # ==================================================
        # ANÁLISE INVESTIA
        # ==================================================

        st.divider()

        st.subheader(
            "🤖 Análise InvestIA"
        )


        col1, col2 = st.columns(
            2
        )


        # --------------------------------------------------
        # JUSTIFICATIVAS
        # --------------------------------------------------

        with col1:

            st.markdown(
                "### 🔎 Principais fatores"
            )


            for reason in result["reasons"]:

                st.write(
                    f"✔ {reason}"
                )


        # --------------------------------------------------
        # RESUMO DE RISCO
        # --------------------------------------------------

        with col2:

            st.markdown(
                "### 🛡️ Gestão de risco"
            )


            st.write(
                f'{risk_icon(result["risk"])} '
                f'**Risco:** {result["risk"]}'
            )


            st.write(
                f'**Score de risco:** '
                f'{result["risk_score"]:.0f}/100'
            )


            st.write(
                f'**Score técnico:** '
                f'{result["technical_score"]:.0f}/100'
            )


        # ==================================================
        # RESUMO FINAL
        # ==================================================

        st.divider()

        st.subheader(
            "📋 Resumo InvestIA"
        )


        st.info(
            f'O ativo **{asset}** apresenta '
            f'Score InvestIA de '
            f'**{result["score"]:.0f}/100**, '
            f'com tendência **{result["trend"]}** '
            f'e recomendação **{result["recommendation"]}**.'
        )


        # ==================================================
        # INFORMAÇÕES TÉCNICAS
        # ==================================================

        with st.expander(
            "🔧 Ver indicadores técnicos"
        ):

            st.write(
                f'**Preço:** '
                f'{format_currency(analysis_data["price"])}'
            )

            st.write(
                f'**MA21:** '
                f'{format_currency(analysis_data["ma21"])}'
            )

            st.write(
                f'**MA200:** '
                f'{format_currency(analysis_data["ma200"])}'
            )

            st.write(
                f'**RSI:** '
                f'{analysis_data["rsi"]:.2f}'
            )

            st.write(
                f'**Volatilidade:** '
                f'{analysis_data["volatility"]:.4f}'
            )


    # ======================================================
    # TRATAMENTO DE ERROS
    # ======================================================

    except Exception as error:

        st.error(
            "Ocorreu um erro durante a análise."
        )

        st.exception(
            error
        )


# ==========================================================
# ESTADO INICIAL
# ==========================================================

else:

    st.info(
        "Digite um ativo e clique em "
        "**🔎 Analisar ativo** para iniciar."
    )
