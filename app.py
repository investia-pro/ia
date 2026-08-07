"""
InvestIA PRO
Aplicação principal

Versão: v0.5.3
"""

import streamlit as st

from market import get_market_data
from indicators import calculate_indicators
from analysis import analyze_asset
from charts import create_price_chart

from utils import (
    validate_data,
    format_currency,
    risk_color
)



# =====================================
# Configuração da página
# =====================================

st.set_page_config(

    page_title="InvestIA PRO",

    page_icon="📈",

    layout="wide"

)



# =====================================
# Cabeçalho
# =====================================

st.title("📈 InvestIA PRO")

st.caption(
    "Análise inteligente de ativos financeiros"
)



# =====================================
# Entrada do usuário
# =====================================


asset = st.text_input(

    "Digite o código do ativo",

    value="PETR4"

)



period = st.selectbox(

    "Período de análise",

    [

        "6mo",

        "1y",

        "2y",

        "5y"

    ],

    index=1

)



analyze_button = st.button(
    "🔎 Analisar ativo"
)



# =====================================
# Execução principal
# =====================================


if analyze_button:


    try:


        with st.spinner(
            "Buscando dados do mercado..."
        ):


            # -----------------------------
            # Mercado
            # -----------------------------

            market_data = get_market_data(

                asset,

                period

            )


            if market_data is None:

                st.error(
                    "Não foi possível obter dados do ativo."
                )

                st.stop()



            # -----------------------------
            # Indicadores
            # -----------------------------


            indicators = calculate_indicators(

                market_data

            )



            # Junta os dados

            analysis_data = {

                **indicators

            }



            if not validate_data(
                analysis_data
            ):

                st.warning(
                    "Dados insuficientes para análise."
                )

                st.stop()



            # -----------------------------
            # IA de análise
            # -----------------------------


            result = analyze_asset(

                analysis_data

            )



            # -----------------------------
            # Dashboard
            # -----------------------------


            st.divider()


            col1, col2, col3 = st.columns(3)



            with col1:

                st.metric(

                    "Preço atual",

                    format_currency(

                        analysis_data["price"]

                    )

                )



            with col2:

                st.metric(

                    "Tendência",

                    result["tendencia"]

                )



            with col3:

                st.metric(

                    "Recomendação",

                    result["recomendacao"]

                )



            st.divider()



            # -----------------------------
            # Gráfico
            # -----------------------------


            st.subheader(
                "📊 Evolução do preço"
            )


            fig = create_price_chart(

                market_data

            )


            st.plotly_chart(

                fig,

                use_container_width=True

            )



            # -----------------------------
            # Análise
            # -----------------------------


            st.subheader(
                "🤖 Análise InvestIA"
            )



            col1, col2 = st.columns(2)



            with col1:


                st.write(
                    "### Indicadores"
                )


                for item in result["justificativas"]:

                    st.write(
                        "✔ ",
                        item
                    )



            with col2:


                st.write(
                    "### Gestão de risco"
                )


                st.write(

                    risk_color(
                        result["risco"]
                    ),

                    result["risco"]

                )



                st.write(

                    "Score InvestIA:",

                    result["score"]

                )



    except Exception as error:


        st.error(
            "Erro inesperado na análise."
        )


        st.exception(error)



else:


    st.info(

        "Digite um ativo e clique em Analisar."

    )
