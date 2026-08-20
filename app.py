"""
InvestIA PRO
Aplicação Principal

Versão: v0.6
Fase: 2.9.7 - Dashboard Integrado e Robusto
"""

import streamlit as st


# ==========================================================
# IMPORTAÇÃO DOS MÓDULOS
# ==========================================================

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
    create_volume_chart,
    create_rsi_chart,
    create_performance_chart,
)

from utils import (
    safe_float,
    validate_analysis_data,
    validate_history,
    format_currency,
    format_percent,
    format_score,
    risk_icon,
    signal_icon,
    trend_icon,
    classification_icon,
    normalize_asset,
    get_result_value,
)


# ==========================================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================================

st.set_page_config(
    page_title="InvestIA PRO",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def get_indicator_value(
    indicators,
    key,
    default=None,
):
    """
    Obtém um indicador de forma segura.
    """

    if not isinstance(
        indicators,
        dict,
    ):
        return default

    value = indicators.get(
        key,
        default,
    )

    if value is None:
        return default

    return value


def get_numeric_indicator(
    indicators,
    key,
    default=None,
):
    """
    Obtém um indicador numérico
    de forma segura.
    """

    value = get_indicator_value(
        indicators,
        key,
        default=None,
    )

    return safe_float(
        value,
        default=default,
    )


def show_error(
    message,
    error=None,
):
    """
    Exibe erro de forma padronizada.
    """

    st.error(
        message
    )

    if error is not None:

        with st.expander(
            "Detalhes técnicos"
        ):

            st.exception(
                error
            )


def safe_metric(
    label,
    value,
    delta=None,
):
    """
    Renderiza um st.metric sem permitir
    que valores inválidos interrompam a página.
    """

    try:

        if value is None:
            value = "N/D"

        st.metric(
            label=label,
            value=value,
            delta=delta,
        )

    except Exception:

        st.metric(
            label=label,
            value="N/D",
        )


def calculate_price_variation(
    history,
):
    """
    Calcula a variação entre os dois
    últimos fechamentos disponíveis.
    """

    if not validate_history(
        history
    ):
        return None

    try:

        if "Close" not in history.columns:
            return None

        close = history["Close"].dropna()

        if len(close) < 2:
            return None

        previous_price = safe_float(
            close.iloc[-2],
            default=None,
        )

        current_price = safe_float(
            close.iloc[-1],
            default=None,
        )

        if (
            previous_price is None
            or current_price is None
            or previous_price == 0
        ):
            return None

        return (
            current_price
            / previous_price
            - 1
        )

    except Exception:

        return None


def get_history_from_prepared_data(
    prepared_data,
):
    """
    Obtém o histórico de forma segura.
    """

    if not isinstance(
        prepared_data,
        dict,
    ):
        return None

    return prepared_data.get(
        "history"
    )


# ==========================================================
# CABEÇALHO
# ==========================================================

st.title(
    "📈 InvestIA PRO"
)

st.caption(
    "Análise inteligente de ativos financeiros"
)


# ==========================================================
# ÁREA DE CONSULTA
# ==========================================================

input_col, period_col, button_col = st.columns(
    [3, 2, 1]
)


with input_col:

    asset_input = st.text_input(
        "Código do ativo",
        value="PETR4",
        max_chars=20,
        placeholder="Ex.: PETR4, VALE3, ITUB4",
    )


with period_col:

    period = st.selectbox(
        "Período de análise",
        options=[
            "6mo",
            "1y",
            "2y",
            "5y",
        ],
        index=1,
    )


with button_col:

    st.write("")

    analyze_button = st.button(
        "🔎 Analisar",
        use_container_width=True,
    )


# ==========================================================
# TELA INICIAL
# ==========================================================

if not analyze_button:

    st.divider()

    st.info(
        "Informe o código de um ativo e clique em "
        "**🔎 Analisar**."
    )

    st.markdown(
        """
### Como utilizar

1. Digite o código do ativo.
2. Escolha o período de análise.
3. Clique em **Analisar**.
4. Consulte o Score InvestIA, os indicadores,
   a tendência, o risco e a recomendação.

**Exemplos:** `PETR4`, `VALE3`, `ITUB4`.
        """
    )

    st.stop()


# ==========================================================
# NORMALIZAÇÃO DO ATIVO
# ==========================================================

asset = normalize_asset(
    asset_input
)


if not asset:

    st.warning(
        "Digite o código de um ativo."
    )

    st.stop()


# ==========================================================
# BUSCA DE DADOS
# ==========================================================

with st.spinner(
    f"Buscando dados de {asset}..."
):

    try:

        market_data = get_market_data(
            asset,
            period,
        )

    except Exception as error:

        show_error(
            "Não foi possível buscar os dados do mercado.",
            error,
        )

        st.stop()


if market_data is None:

    st.error(
        f"Não foi possível obter dados para {asset}."
    )

    st.stop()


# ==========================================================
# PREPARAÇÃO DOS DADOS
# ==========================================================

with st.spinner(
    "Preparando dados do mercado..."
):

    try:

        prepared_data = prepare_market_data(
            market_data
        )

    except Exception as error:

        show_error(
            "Erro ao preparar os dados do ativo.",
            error,
        )

        st.stop()


if prepared_data is None:

    st.error(
        "Os dados do mercado não puderam ser preparados."
    )

    st.stop()


# ==========================================================
# HISTÓRICO
# ==========================================================

history = get_history_from_prepared_data(
    prepared_data
)


if not validate_history(
    history
):

    st.error(
        "O histórico de preços não está disponível."
    )

    st.stop()


# ==========================================================
# PREÇO ATUAL
# ==========================================================

try:

    price = get_current_price(
        prepared_data
    )

except Exception as error:

    show_error(
        "Não foi possível determinar o preço atual.",
        error,
    )

    st.stop()


price = safe_float(
    price,
    default=None,
)


if price is None:

    st.error(
        "O preço atual retornado é inválido."
    )

    st.stop()


# ==========================================================
# INDICADORES
# ==========================================================

with st.spinner(
    "Calculando indicadores técnicos..."
):

    try:

        indicators = calculate_indicators(
            prepared_data
        )

    except Exception as error:

        show_error(
            "Erro ao calcular os indicadores técnicos.",
            error,
        )

        st.stop()


if not isinstance(
    indicators,
    dict,
):

    st.error(
        "Os indicadores não foram calculados corretamente."
    )

    st.stop()


# ==========================================================
# DADOS PARA ANÁLISE
# ==========================================================

ma21 = get_numeric_indicator(
    indicators,
    "ma21",
)

ma200 = get_numeric_indicator(
    indicators,
    "ma200",
)

rsi = get_numeric_indicator(
    indicators,
    "rsi",
)

volatility = get_numeric_indicator(
    indicators,
    "volatility",
)


analysis_data = {

    "price":
        price,

    "ma21":
        ma21,

    "ma200":
        ma200,

    "rsi":
        rsi,

    "volatility":
        volatility,
}


# ==========================================================
# VALIDAÇÃO DOS DADOS TÉCNICOS
# ==========================================================

if not validate_analysis_data(
    analysis_data
):

    st.error(
        "Os dados técnicos são insuficientes para realizar "
        "a análise do ativo."
    )

    missing = []

    for key in [
        "price",
        "ma21",
        "ma200",
        "rsi",
    ]:

        if analysis_data.get(key) is None:

            missing.append(
                key.upper()
            )

    if missing:

        st.warning(
            "Dados indisponíveis: "
            + ", ".join(missing)
        )

    st.stop()


# ==========================================================
# MOTOR DE ANÁLISE
# ==========================================================

with st.spinner(
    "Executando análise InvestIA..."
):

    try:

        result = analyze_asset(
            analysis_data,
            asset,
        )

    except Exception as error:

        show_error(
            "Erro ao executar a análise InvestIA.",
            error,
        )

        st.stop()


if not isinstance(
    result,
    dict,
):

    st.error(
        "A análise não retornou um resultado válido."
    )

    st.stop()


# ==========================================================
# EXTRAÇÃO DOS RESULTADOS
# ==========================================================

score = get_result_value(
    result,
    "score",
    default=0,
)

classification = get_result_value(
    result,
    "classification",
    default="NEUTRO",
)

signal = get_result_value(
    result,
    "qualified_signal",
    "signal",
    default="NEUTRO",
)

signal_level = get_result_value(
    result,
    "signal_level",
    default="Aguardar",
)

trend = get_result_value(
    result,
    "trend",
    "tendencia",
    default="Neutra",
)

risk = get_result_value(
    result,
    "risk",
    "risco",
    default="Moderado",
)

recommendation = get_result_value(
    result,
    "recommendation",
    "recomendacao",
    default="Acompanhar",
)

rsi_status = get_result_value(
    result,
    "rsi_status",
    default="Indisponível",
)

reasons = get_result_value(
    result,
    "reasons",
    "justificativas",
    default=[],
)

breakdown = get_result_value(
    result,
    "breakdown",
    default={},
)

executive_summary = get_result_value(
    result,
    "executive_summary",
    default="",
)


# ==========================================================
# VARIAÇÃO DO PREÇO
# ==========================================================

price_variation = calculate_price_variation(
    history
)


variation_text = None

if price_variation is not None:

    variation_text = format_percent(
        price_variation
    )


# ==========================================================
# CABEÇALHO DA ANÁLISE
# ==========================================================

st.divider()

st.header(
    f"📊 Análise: {asset}"
)


# ==========================================================
# CARDS PRINCIPAIS
# ==========================================================

card1, card2, card3, card4 = st.columns(
    4
)


with card1:

    safe_metric(
        "Preço atual",
        format_currency(
            price
        ),
        variation_text,
    )


with card2:

    safe_metric(
        "Score InvestIA",
        format_score(
            score
        ),
    )


with card3:

    safe_metric(
        "Tendência",
        f"{trend_icon(trend)} {trend}",
    )


with card4:

    safe_metric(
        "Recomendação",
        recommendation,
    )


# ==========================================================
# STATUS GERAL
# ==========================================================

st.info(
    f"**{classification_icon(classification)} Classificação:** "
    f"{classification} "
    f"| **{signal_icon(signal)} Sinal:** "
    f"{signal} "
    f"| **Nível:** {signal_level} "
    f"| **{risk_icon(risk)} Risco:** {risk}"
)


# ==========================================================
# RESUMO EXECUTIVO
# ==========================================================

st.divider()

st.subheader(
    "🤖 Resumo Executivo"
)


if executive_summary:

    st.success(
        executive_summary
    )

else:

    st.info(
        "Resumo executivo não disponível."
    )


# ==========================================================
# INDICADORES TÉCNICOS
# ==========================================================

st.divider()

st.subheader(
    "📈 Indicadores Técnicos"
)


indicator1, indicator2, indicator3, indicator4 = st.columns(
    4
)


with indicator1:

    safe_metric(
        "MA21",
        format_currency(
            ma21
        ),
    )


with indicator2:

    safe_metric(
        "MA200",
        format_currency(
            ma200
        ),
    )


with indicator3:

    rsi_text = (
        f"{rsi:.2f}"
        if rsi is not None
        else "N/D"
    )

    safe_metric(
        "RSI",
        rsi_text,
    )


with indicator4:

    volatility_text = format_percent(
        volatility
    )

    safe_metric(
        "Volatilidade",
        volatility_text,
    )


# ==========================================================
# SCORE INVESTIA
# ==========================================================

st.divider()

st.subheader(
    "🧠 Composição do Score InvestIA"
)

st.caption(
    "O Score InvestIA é calculado a partir da posição "
    "do preço em relação às médias móveis e da leitura do RSI."
)


# ==========================================================
# BASE
# ==========================================================

base_points = 50


if isinstance(
    breakdown,
    dict,
):

    base_points = breakdown.get(
        "base",
        50,
    )


try:

    base_points = int(
        round(
            safe_float(
                base_points,
                default=50,
            )
        )
    )

except Exception:

    base_points = 50


st.write(
    f"**Score Base:** {base_points:+d} pontos"
)


# ==========================================================
# COMPONENTES DO SCORE
# ==========================================================

score_col1, score_col2, score_col3 = st.columns(
    3
)


def get_breakdown_component(
    breakdown_data,
    component,
):
    """
    Obtém os dados de um componente
    do breakdown do Score.
    """

    default_data = {

        "points": 0,
        "signal": "Neutro",
        "reason": "Sem informação.",
    }

    if not isinstance(
        breakdown_data,
        dict,
    ):
        return default_data

    component_data = breakdown_data.get(
        component,
        {}
    )

    if not isinstance(
        component_data,
        dict,
    ):
        return default_data

    return {

        "points":
            component_data.get(
                "points",
                0,
            ),

        "signal":
            component_data.get(
                "signal",
                "Neutro",
            ),

        "reason":
            component_data.get(
                "reason",
                "Sem informação.",
            ),
    }


ma21_component = get_breakdown_component(
    breakdown,
    "ma21",
)

ma200_component = get_breakdown_component(
    breakdown,
    "ma200",
)

rsi_component = get_breakdown_component(
    breakdown,
    "rsi",
)


with score_col1:

    ma21_points = safe_float(
        ma21_component["points"],
        default=0,
    )

    st.markdown(
        "### 📏 MA21"
    )

    safe_metric(
        "Contribuição",
        f"{int(round(ma21_points)):+d} pts",
    )

    st.write(
        f"**Sinal:** {ma21_component['signal']}"
    )

    st.caption(
        ma21_component["reason"]
    )


with score_col2:

    ma200_points = safe_float(
        ma200_component["points"],
        default=0,
    )

    st.markdown(
        "### 📐 MA200"
    )

    safe_metric(
        "Contribuição",
        f"{int(round(ma200_points)):+d} pts",
    )

    st.write(
        f"**Sinal:** {ma200_component['signal']}"
    )

    st.caption(
        ma200_component["reason"]
    )


with score_col3:

    rsi_points = safe_float(
        rsi_component["points"],
        default=0,
    )

    st.markdown(
        "### 📊 RSI"
    )

    safe_metric(
        "Contribuição",
        f"{int(round(rsi_points)):+d} pts",
    )

    st.write(
        f"**Sinal:** {rsi_component['signal']}"
    )

    st.caption(
        rsi_component["reason"]
    )


# ==========================================================
# SCORE FINAL
# ==========================================================

raw_score = None


if isinstance(
    breakdown,
    dict,
):

    raw_score = breakdown.get(
        "raw_score"
    )


if raw_score is not None:

    raw_score = safe_float(
        raw_score,
        default=None,
    )


if raw_score is not None:

    st.success(
        f"**Score final: {format_score(score)}** "
        f"| Pontuação bruta: {raw_score:.0f}"
    )

else:

    st.success(
        f"**Score final: {format_score(score)}**"
    )


# ==========================================================
# GRÁFICOS
# ==========================================================

st.divider()

st.subheader(
    "📊 Análise Gráfica"
)


# ==========================================================
# PREÇO
# ==========================================================

try:

    price_chart = create_price_chart(
        history
    )

    if price_chart is not None:

        st.plotly_chart(
            price_chart,
            use_container_width=True,
        )

    else:

        st.warning(
            "Não foi possível gerar o gráfico de preços."
        )

except Exception as error:

    show_error(
        "Erro ao gerar o gráfico de preços.",
        error,
    )


# ==========================================================
# RSI E VOLUME
# ==========================================================

chart_col1, chart_col2 = st.columns(
    2
)


with chart_col1:

    try:

        rsi_chart = create_rsi_chart(
            history
        )

        if rsi_chart is not None:

            st.plotly_chart(
                rsi_chart,
                use_container_width=True,
            )

        else:

            st.info(
                "Dados insuficientes para o gráfico do RSI."
            )

    except Exception:

        st.info(
            "O gráfico do RSI não está disponível."
        )


with chart_col2:

    try:

        volume_chart = create_volume_chart(
            history
        )

        if volume_chart is not None:

            st.plotly_chart(
                volume_chart,
                use_container_width=True,
            )

        else:

            st.info(
                "Dados de volume não disponíveis."
            )

    except Exception:

        st.info(
            "O gráfico de volume não está disponível."
        )


# ==========================================================
# PERFORMANCE
# ==========================================================

try:

    performance_chart = create_performance_chart(
        history
    )

    if performance_chart is not None:

        st.plotly_chart(
            performance_chart,
            use_container_width=True,
        )

except Exception:

    pass


# ==========================================================
# ANÁLISE DETALHADA
# ==========================================================

st.divider()

st.subheader(
    "🔎 Análise Detalhada"
)


detail_col1, detail_col2 = st.columns(
    2
)


# ==========================================================
# FUNDAMENTAÇÃO
# ==========================================================

with detail_col1:

    st.markdown(
        "### 📋 Fundamentação"
    )


    if isinstance(
        reasons,
        list,
    ) and reasons:

        for reason in reasons:

            if reason:

                st.write(
                    f"✔ {reason}"
                )

    else:

        st.info(
            "Nenhuma justificativa detalhada foi retornada."
        )


# ==========================================================
# GESTÃO DE RISCO
# ==========================================================

with detail_col2:

    st.markdown(
        "### 🛡️ Gestão de Risco"
    )

    st.write(
        f"**Risco:** "
        f"{risk_icon(risk)} {risk}"
    )

    st.write(
        f"**Tendência:** "
        f"{trend_icon(trend)} {trend}"
    )

    st.write(
        f"**RSI:** {rsi_status}"
    )

    st.write(
        f"**Sinal:** "
        f"{signal_icon(signal)} {signal}"
    )

    st.write(
        f"**Score:** "
        f"{format_score(score)}"
    )

    st.write(
        f"**Recomendação:** "
        f"{recommendation}"
    )


# ==========================================================
# RESUMO FINAL
# ==========================================================

st.divider()

st.subheader(
    "📌 Resumo da Análise"
)


summary_col1, summary_col2 = st.columns(
    2
)


with summary_col1:

    st.write(
        f"**Ativo:** {asset}"
    )

    st.write(
        f"**Preço Atual:** "
        f"{format_currency(price)}"
    )

    st.write(
        f"**Score InvestIA:** "
        f"{format_score(score)}"
    )

    st.write(
        f"**Classificação:** "
        f"{classification_icon(classification)} "
        f"{classification}"
    )


with summary_col2:

    st.write(
        f"**Tendência:** "
        f"{trend_icon(trend)} {trend}"
    )

    st.write(
        f"**Sinal:** "
        f"{signal_icon(signal)} {signal}"
    )

    st.write(
        f"**Risco:** "
        f"{risk_icon(risk)} {risk}"
    )

    st.write(
        f"**Recomendação:** "
        f"{recommendation}"
    )


# ==========================================================
# RODAPÉ
# ==========================================================

st.divider()

st.caption(
    "InvestIA PRO v0.6 | "
    "Fase 2.9.7 | "
    "Análise técnica baseada em indicadores históricos."
)
