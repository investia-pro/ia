"""
InvestIA PRO
Aplicação principal

Versão: v0.6
Fase: Integração e estabilização
"""

import streamlit as st

from market import (
    get_market_data,
    prepare_market_data,
    get_current_price,
)

from indicators import (
    calculate_indicators,
)

from analysis import (
    analyze_asset,
)

from charts import (
    create_price_chart,
)

from utils import (
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
    [3, 1]
)


with col_input:

    asset = st.text_input(
        "Digite o código do ativo",
        value="PETR4",
        max_chars=20,
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
# FUNÇÕES AUXILIARES
# ==========================================================

def normalize_asset_input(asset):
    """
    Normaliza o código informado pelo usuário.
    """

    if asset is None:
        return ""

    return (
        str(asset)
        .strip()
        .upper()
        .replace(" ", "")
    )


def get_indicator_value(
    indicators,
    key,
    default=None,
):
    """
    Obtém um indicador com segurança.
    """

    if not isinstance(
        indicators,
        dict,
    ):
        return default

    return indicators.get(
        key,
        default,
    )


def get_analysis_value(
    result,
    *keys,
    default=None,
):
    """
    Permite trabalhar com diferentes
    nomenclaturas de retorno do analysis.py.
    """

    if not isinstance(
        result,
        dict,
    ):
        return default

    for key in keys:

        if key in result:

            return result[key]

    return default


# ==========================================================
# EXECUÇÃO PRINCIPAL
# ==========================================================

if analyze_button:

    # ======================================================
    # VALIDAÇÃO DO ATIVO
    # ======================================================

    asset = normalize_asset_input(
        asset
    )

    if not asset:

        st.warning(
            "Digite o código de um ativo."
        )

        st.stop()

    # ======================================================
    # BUSCA DOS DADOS
    # ======================================================

    with st.spinner(
        "Buscando dados do mercado..."
    ):

        market_data = get_market_data(
            asset,
            period,
        )

    # ======================================================
    # VALIDAÇÃO DO RETORNO
    # ======================================================

    if market_data is None:

        st.error(
            f"Não foi possível obter "
            f"dados para {asset}."
        )

        st.info(
            "Verifique o código do ativo "
            "e tente novamente."
        )

        st.stop()

    # ======================================================
    # NORMALIZAÇÃO
    # ======================================================

    prepared_data = prepare_market_data(
        market_data
    )

    if prepared_data is None:

        st.error(
            "Os dados recebidos do mercado "
            "não puderam ser preparados "
            "para análise."
        )

        st.stop()

    # ======================================================
    # HISTÓRICO
    # ======================================================

    history = prepared_data.get(
        "history"
    )

    if history is None:

        st.error(
            "O histórico do ativo não "
            "foi encontrado."
        )

        st.stop()

    if history.empty:

        st.error(
            "O histórico do ativo está vazio."
        )

        st.stop()

    # ======================================================
    # PREÇO
    # ======================================================

    price = get_current_price(
        prepared_data
    )

    if price is None:

        st.error(
            "Não foi possível determinar "
            "o preço atual do ativo."
        )

        st.stop()

    # ======================================================
    # INDICADORES
    # ======================================================

    with st.spinner(
        "Calculando indicadores técnicos..."
    ):

        try:

            # IMPORTANTE:
            # indicators.py espera o objeto completo
            # contendo "history".

            indicators = calculate_indicators(
                prepared_data
            )

        except Exception as error:

            st.error(
                "Erro ao calcular os "
                "indicadores técnicos."
            )

            st.exception(
                error
            )

            st.stop()

    # ======================================================
    # VALIDAÇÃO DOS INDICADORES
    # ======================================================

    if indicators is None:

        st.error(
            "Não foi possível calcular "
            "os indicadores."
        )

        st.stop()

    if not isinstance(
        indicators,
        dict,
    ):

        st.error(
            "O módulo de indicadores "
            "retornou um formato inválido."
        )

        st.stop()

    # ======================================================
    # CONSOLIDAÇÃO DOS DADOS
    # ======================================================

    analysis_data = {

        "price":
            price,

        "rsi":
            get_indicator_value(
                indicators,
                "rsi",
            ),

        "ma21":
            get_indicator_value(
                indicators,
                "ma21",
            ),

        "ma200":
            get_indicator_value(
                indicators,
                "ma200",
            ),

        "volatility":
            get_indicator_value(
                indicators,
                "volatility",
            ),
    }

    # ======================================================
    # VALIDAÇÃO FINAL
    # ======================================================

    if not validate_analysis_data(
        analysis_data
    ):

        st.warning(
            "Os dados disponíveis não são "
            "suficientes para realizar "
            "uma análise confiável."
        )

        st.subheader(
            "Diagnóstico dos dados"
        )

        diagnostic_col1, diagnostic_col2 = (
            st.columns(2)
        )

        with diagnostic_col1:

            st.write(
                "### Mercado"
            )

            st.success(
                "✓ Dados de mercado "
                "disponíveis."
            )

            st.write(
                "### Histórico"
            )

            if len(history) >= 200:

                st.success(
                    "✓ Histórico suficiente."
                )

            else:

                st.warning(
                    f"⚠ Histórico possui "
                    f"{len(history)} períodos. "
                    f"São recomendados pelo "
                    f"menos 200."
                )

        with diagnostic_col2:

            st.write(
                "### Estrutura"
            )

            required_fields = [
                "price",
                "rsi",
                "ma21",
                "ma200",
                "volatility",
            ]

            missing_fields = [
                field
                for field in required_fields
                if analysis_data.get(field) is None
            ]

            if missing_fields:

                st.error(
                    "✗ Campos ausentes: "
                    + ", ".join(
                        missing_fields
                    )
                )

            else:

                st.success(
                    "✓ Estrutura válida."
                )

            st.write(
                "### Indicadores"
            )

            if missing_fields:

                st.error(
                    "✗ Indicadores "
                    "incompletos."
                )

            else:

                st.success(
                    "✓ Indicadores válidos."
                )

        st.stop()

    # ======================================================
    # ANÁLISE
    # ======================================================

    with st.spinner(
        "Executando análise InvestIA..."
    ):

        try:

            result = analyze_asset(
                analysis_data
            )

        except Exception as error:

            st.error(
                "Erro ao executar a "
                "análise do ativo."
            )

            st.exception(
                error
            )

            st.stop()

    if result is None:

        st.error(
            "O motor de análise não "
            "retornou um resultado."
        )

        st.stop()

    # ======================================================
    # RESULTADOS DA ANÁLISE
    # ======================================================

    score = get_analysis_value(
        result,
        "score",
        default=0,
    )

    trend = get_analysis_value(
        result,
        "trend",
        "tendencia",
        default="Neutra",
    )

    recommendation = get_analysis_value(
        result,
        "recommendation",
        "recomendacao",
        default="Aguardar",
    )

    risk = get_analysis_value(
        result,
        "risk",
        "risco",
        default="Moderado",
    )

    reasons = get_analysis_value(
        result,
        "reasons",
        "justificativas",
        default=[],
    )

    # ======================================================
    # TÍTULO DA ANÁLISE
    # ======================================================

    st.divider()

    st.header(
        f"📊 Análise do ativo: {asset}"
    )

    # ======================================================
    # CARDS PRINCIPAIS
    # ======================================================

    col1, col2, col3, col4 = st.columns(
        4
    )

    with col1:

        st.metric(
            "Preço atual",
            format_currency(
                price
            ),
        )

    with col2:

        st.metric(
            "Score InvestIA",
            f"{score}/100",
        )

    with col3:

        st.metric(
            "Tendência",
            str(trend),
        )

    with col4:

        st.metric(
            "Recomendação",
            str(recommendation),
        )

    # ======================================================
    # INDICADORES
    # ======================================================

    st.divider()

    st.subheader(
        "📈 Indicadores técnicos"
    )

    ind1, ind2, ind3, ind4 = st.columns(
        4
    )

    with ind1:

        st.metric(
            "MA21",
            format_currency(
                analysis_data["ma21"]
            ),
        )

    with ind2:

        st.metric(
            "MA200",
            format_currency(
                analysis_data["ma200"]
            ),
        )

    with ind3:

        st.metric(
            "RSI",
            f'{analysis_data["rsi"]:.2f}',
        )

    with ind4:

        volatility_percent = (
            analysis_data["volatility"]
            * 100
        )

        st.metric(
            "Volatilidade",
            f"{volatility_percent:.2f}%",
        )

    # ======================================================
    # GRÁFICO
    # ======================================================

    st.divider()

    st.subheader(
        "📊 Evolução do preço"
    )

    try:

        fig = create_price_chart(
            history
        )

        if fig is not None:

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

        else:

            st.warning(
                "Não foi possível gerar "
                "o gráfico."
            )

    except Exception as error:

        st.warning(
            "O gráfico não pôde ser "
            "gerado."
        )

        st.exception(
            error
        )

    # ======================================================
    # ANÁLISE INVESTIA
    # ======================================================

    st.divider()

    st.subheader(
        "🤖 Análise InvestIA"
    )

    analysis_col1, analysis_col2 = (
        st.columns(2)
    )

    # ======================================================
    # JUSTIFICATIVAS
    # ======================================================

    with analysis_col1:

        st.write(
            "### Indicadores"
        )

        if reasons:

            for reason in reasons:

                st.write(
                    f"✔ {reason}"
                )

        else:

            st.info(
                "Nenhuma justificativa "
                "foi retornada."
            )

    # ======================================================
    # RISCO
    # ======================================================

    with analysis_col2:

        st.write(
            "### Gestão de risco"
        )

        st.write(
            f"{risk_icon(risk)} {risk}"
        )

        st.write(
            f"**Score InvestIA:** "
            f"{score}/100"
        )

    # ======================================================
    # RESUMO
    # ======================================================

    st.divider()

    st.subheader(
        "📋 Resumo da análise"
    )

    summary_col1, summary_col2 = (
        st.columns(2)
    )

    with summary_col1:

        st.write(
            f"**Ativo:** {asset}"
        )

        st.write(
            f"**Preço:** "
            f"{format_currency(price)}"
        )

        st.write(
            f"**Tendência:** {trend}"
        )

    with summary_col2:

        st.write(
            f"**Score:** {score}/100"
        )

        st.write(
            f"**Recomendação:** "
            f"{recommendation}"
        )

        st.write(
            f"**Risco:** "
            f"{risk_icon(risk)} {risk}"
        )

else:

    st.info(
        "Digite um ativo e clique em "
        "🔎 Analisar ativo."
    )
