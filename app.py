"""
InvestIA PRO
Aplicação principal

Versão: v0.6
Fase: 2.4 - Explicabilidade do Score
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
# CONFIGURAÇÃO
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
# ENTRADA
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
# EXECUÇÃO
# ==========================================================

if analyze_button:

    asset = normalize_asset_input(
        asset
    )

    if not asset:

        st.warning(
            "Digite o código de um ativo."
        )

        st.stop()

    # ======================================================
    # MERCADO
    # ======================================================

    with st.spinner(
        "Buscando dados do mercado..."
    ):

        market_data = get_market_data(
            asset,
            period,
        )

    if market_data is None:

        st.error(
            f"Não foi possível obter "
            f"dados para {asset}."
        )

        st.stop()

    # ======================================================
    # PREPARAÇÃO
    # ======================================================

    prepared_data = prepare_market_data(
        market_data
    )

    if prepared_data is None:

        st.error(
            "Os dados do mercado "
            "não puderam ser preparados."
        )

        st.stop()

    history = prepared_data.get(
        "history"
    )

    if history is None or history.empty:

        st.error(
            "Histórico do ativo não encontrado."
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
            "o preço atual."
        )

        st.stop()

    # ======================================================
    # INDICADORES
    # ======================================================

    with st.spinner(
        "Calculando indicadores técnicos..."
    ):

        try:

            indicators = calculate_indicators(
                prepared_data
            )

        except Exception as error:

            st.error(
                "Erro ao calcular "
                "os indicadores."
            )

            st.exception(
                error
            )

            st.stop()

    if indicators is None:

        st.error(
            "Os indicadores não foram calculados."
        )

        st.stop()

    # ======================================================
    # DADOS DE ANÁLISE
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
    # VALIDAÇÃO
    # ======================================================

    if not validate_analysis_data(
        analysis_data
    ):

        st.warning(
            "Dados insuficientes "
            "para análise."
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
                "Erro ao executar "
                "a análise."
            )

            st.exception(
                error
            )

            st.stop()

    if result is None:

        st.error(
            "A análise não retornou resultado."
        )

        st.stop()

    # ======================================================
    # RESULTADOS
    # ======================================================

    score = get_analysis_value(
        result,
        "score",
        default=0,
    )

    classification = get_analysis_value(
        result,
        "classification",
        default="NEUTRO",
    )

    signal = get_analysis_value(
        result,
        "signal",
        default="NEUTRO",
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

    breakdown = get_analysis_value(
        result,
        "breakdown",
        default={},
    )

    # ======================================================
    # TÍTULO
    # ======================================================

    st.divider()

    st.header(
        f"📊 Análise do ativo: {asset}"
    )

    # ======================================================
    # CARDS
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
    # CLASSIFICAÇÃO
    # ======================================================

    st.info(
        f"**Classificação:** {classification}  "
        f"| **Sinal:** {signal}"
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
    # EXPLICABILIDADE DO SCORE
    # ======================================================

    st.divider()

    st.subheader(
        "🧠 Como o Score foi calculado"
    )

    st.caption(
        "O Score InvestIA começa em 50 pontos "
        "e recebe ajustes conforme os indicadores técnicos."
    )

    # ======================================================
    # BASE
    # ======================================================

    base_points = 50

    if isinstance(
        breakdown,
        dict,
    ):

        base_points = breakdown.get(
            "base",
            50,
        )

    st.write(
        f"**Base:** {base_points:+d} pontos"
    )

    # ======================================================
    # BREAKDOWN
    # ======================================================

    bd1, bd2, bd3 = st.columns(
        3
    )

    # ------------------------------------------------------
    # MA21
    # ------------------------------------------------------

    with bd1:

        ma21_data = {}

        if isinstance(
            breakdown,
            dict,
        ):

            ma21_data = breakdown.get(
                "ma21",
                {},
            )

        ma21_points = ma21_data.get(
            "points",
            0,
        )

        ma21_signal = ma21_data.get(
            "signal",
            "Neutro",
        )

        ma21_reason = ma21_data.get(
            "reason",
            "Sem informação.",
        )

        st.markdown(
            "### 📏 MA21"
        )

        st.metric(
            "Contribuição",
            f"{ma21_points:+d} pts",
        )

        st.write(
            f"**Sinal:** {ma21_signal}"
        )

        st.caption(
            ma21_reason
        )

    # ------------------------------------------------------
    # MA200
    # ------------------------------------------------------

    with bd2:

        ma200_data = {}

        if isinstance(
            breakdown,
            dict,
        ):

            ma200_data = breakdown.get(
                "ma200",
                {},
            )

        ma200_points = ma200_data.get(
            "points",
            0,
        )

        ma200_signal = ma200_data.get(
            "signal",
            "Neutro",
        )

        ma200_reason = ma200_data.get(
            "reason",
            "Sem informação.",
        )

        st.markdown(
            "### 📐 MA200"
        )

        st.metric(
            "Contribuição",
            f"{ma200_points:+d} pts",
        )

        st.write(
            f"**Sinal:** {ma200_signal}"
        )

        st.caption(
            ma200_reason
        )

    # ------------------------------------------------------
    # RSI
    # ------------------------------------------------------

    with bd3:

        rsi_data = {}

        if isinstance(
            breakdown,
            dict,
        ):

            rsi_data = breakdown.get(
                "rsi",
                {},
            )

        rsi_points = rsi_data.get(
            "points",
            0,
        )

        rsi_signal = rsi_data.get(
            "signal",
            "Neutro",
        )

        rsi_reason = rsi_data.get(
            "reason",
            "Sem informação.",
        )

        st.markdown(
            "### 📊 RSI"
        )

        st.metric(
            "Contribuição",
            f"{rsi_points:+d} pts",
        )

        st.write(
            f"**Sinal:** {rsi_signal}"
        )

        st.caption(
            rsi_reason
        )

    # ======================================================
    # SCORE FINAL
    # ======================================================

    st.write("")

    raw_score = None

    if isinstance(
        breakdown,
        dict,
    ):

        raw_score = breakdown.get(
            "raw_score"
        )

    if raw_score is not None:

        st.success(
            f"**Score final: {score}/100** "
            f"(cálculo bruto: {raw_score})"
        )

    else:

        st.success(
            f"**Score final: {score}/100**"
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
            "O gráfico não pôde ser gerado."
        )

        st.exception(
            error
        )

    # ======================================================
    # ANÁLISE
    # ======================================================

    st.divider()

    st.subheader(
        "🤖 Análise InvestIA"
    )

    analysis_col1, analysis_col2 = (
        st.columns(2)
    )

    with analysis_col1:

        st.write(
            "### Justificativas"
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

    with analysis_col2:

        st.write(
            "### Gestão de risco"
        )

        st.write(
            f"{risk_icon(risk)} {risk}"
        )

        st.write(
            f"**Score:** {score}/100"
        )

        st.write(
            f"**Sinal:** {signal}"
        )

        st.write(
            f"**Recomendação:** "
            f"{recommendation}"
        )

    # ======================================================
    # RESUMO
    # ======================================================

    st.divider()

    st.subheader(
        "📋 Resumo"
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
            f"**Classificação:** "
            f"{classification}"
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
