"""
InvestIA PRO
Aplicação principal

Versão: v0.6
Fase: 2.7.2 - Gestão de Risco e Sinal
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

    if not isinstance(indicators, dict):
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
    Obtém valores do resultado da análise.
    """

    if not isinstance(result, dict):
        return default

    for key in keys:

        if key in result:
            return result[key]

    return default


def safe_int(value, default=0):
    """
    Converte valor para inteiro com segurança.
    """

    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def risk_description(risk):
    """
    Descrição operacional do nível de risco.
    """

    descriptions = {
        "Baixo": (
            "Baixa volatilidade relativa. "
            "O comportamento recente apresenta "
            "menor nível de oscilação."
        ),

        "Moderado": (
            "Volatilidade intermediária. "
            "O ativo exige acompanhamento regular "
            "antes de uma decisão."
        ),

        "Alto": (
            "Alta volatilidade. "
            "Movimentos de preço podem ser mais intensos "
            "e exigem maior controle de risco."
        ),
    }

    return descriptions.get(
        risk,
        "Nível de risco não identificado.",
    )


def signal_description(
    recommendation,
    risk,
):
    """
    Interpretação operacional do sinal.
    """

    if recommendation == "Compra":

        if risk == "Alto":
            return (
                "Cenário favorável, porém com "
                "risco elevado. Exige maior cautela."
            )

        return (
            "Cenário técnico favorável ao movimento "
            "de compra."
        )

    if recommendation == "Compra Moderada":

        return (
            "Cenário parcialmente favorável. "
            "A entrada deve considerar confirmação."
        )

    if recommendation == "Venda":

        if risk == "Alto":
            return (
                "Cenário desfavorável com elevada "
                "volatilidade."
            )

        return (
            "Cenário técnico desfavorável "
            "ao movimento de alta."
        )

    if recommendation == "Venda Moderada":

        return (
            "Cenário parcialmente desfavorável. "
            "Requer confirmação antes de uma decisão."
        )

    return (
        "Os indicadores não apresentam "
        "força suficiente para uma decisão."
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
# EXECUÇÃO
# ==========================================================

if analyze_button:

    asset = normalize_asset_input(
        asset
    )

    # ======================================================
    # VALIDAÇÃO
    # ======================================================

    if not asset:

        st.warning(
            "Digite o código de um ativo."
        )

        st.stop()


    # ======================================================
    # BUSCA DE DADOS
    # ======================================================

    with st.spinner(
        "Buscando dados do mercado..."
    ):

        try:

            market_data = get_market_data(
                asset,
                period,
            )

        except Exception as error:

            st.error(
                "Erro ao buscar os dados do mercado."
            )

            st.exception(error)

            st.stop()


    if market_data is None:

        st.error(
            f"Não foi possível obter dados para {asset}."
        )

        st.stop()


    # ======================================================
    # PREPARAÇÃO
    # ======================================================

    try:

        prepared_data = prepare_market_data(
            market_data
        )

    except Exception as error:

        st.error(
            "Erro ao preparar os dados do mercado."
        )

        st.exception(error)

        st.stop()


    if prepared_data is None:

        st.error(
            "Os dados do mercado não puderam ser preparados."
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
            "Histórico do ativo não encontrado."
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

    try:

        price = get_current_price(
            prepared_data
        )

    except Exception:

        price = None


    if price is None:

        try:

            price = float(
                history["Close"]
                .dropna()
                .iloc[-1]
            )

        except Exception:

            price = None


    if price is None:

        st.error(
            "Não foi possível determinar o preço atual."
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
                "Erro ao calcular os indicadores técnicos."
            )

            st.exception(error)

            st.stop()


    if indicators is None:

        st.error(
            "Os indicadores não foram calculados."
        )

        st.stop()


    # ======================================================
    # DADOS PARA ANÁLISE
    # ======================================================

    analysis_data = {

        "price": price,

        "rsi": get_indicator_value(
            indicators,
            "rsi",
        ),

        "ma21": get_indicator_value(
            indicators,
            "ma21",
        ),

        "ma200": get_indicator_value(
            indicators,
            "ma200",
        ),

        "volatility": get_indicator_value(
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

        st.error(
            "Os dados técnicos são insuficientes "
            "para realizar a análise."
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
                analysis_data,
                asset,
            )

        except TypeError:

            try:

                result = analyze_asset(
                    analysis_data
                )

            except Exception as error:

                st.error(
                    "Erro ao executar a análise InvestIA."
                )

                st.exception(error)

                st.stop()

        except Exception as error:

            st.error(
                "Erro ao executar a análise InvestIA."
            )

            st.exception(error)

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


    qualified_signal = get_analysis_value(
        result,
        "qualified_signal",
        default=signal,
    )


    signal_level = get_analysis_value(
        result,
        "signal_level",
        default="Neutro",
    )


    signal_icon = get_analysis_value(
        result,
        "signal_icon",
        default="🟡",
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


    risk_points = safe_int(
        get_analysis_value(
            result,
            "risk_score",
            default=0,
        )
    )


    rsi_status = get_analysis_value(
        result,
        "rsi_status",
        default="Neutro",
    )


    reasons = get_analysis_value(
        result,
        "reasons",
        "justificativas",
        default=[],
    )


    alerts = get_analysis_value(
        result,
        "alerts",
        default=[],
    )


    breakdown = get_analysis_value(
        result,
        "breakdown",
        default={},
    )


    executive_summary = get_analysis_value(
        result,
        "executive_summary",
        default="",
    )


    # ======================================================
    # CABEÇALHO
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
            format_currency(price),
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
    # SINAL OPERACIONAL
    # ======================================================

    st.divider()

    st.subheader(
        "🎯 Sinal Operacional"
    )


    sig1, sig2, sig3 = st.columns(
        3
    )


    with sig1:

        st.metric(
            "Sinal",
            f"{signal_icon} {qualified_signal}",
        )


    with sig2:

        st.metric(
            "Nível",
            str(signal_level),
        )


    with sig3:

        st.metric(
            "Risco",
            f"{risk_icon(risk)} {risk}",
        )


    st.info(
        signal_description(
            recommendation,
            risk,
        )
    )


    # ======================================================
    # CLASSIFICAÇÃO
    # ======================================================

    st.info(
        f"**Classificação:** {classification} "
        f"| **Sinal:** {signal} "
        f"| **Nível:** {signal_icon} {signal_level}"
    )


    # ======================================================
    # GESTÃO DE RISCO
    # ======================================================

    st.divider()

    st.subheader(
        "🛡️ Gestão de Risco"
    )


    risk1, risk2 = st.columns(
        [1, 2]
    )


    with risk1:

        st.metric(
            "Nível de risco",
            f"{risk_icon(risk)} {risk}",
        )


        st.metric(
            "Índice de risco",
            f"{risk_points}/100",
        )


    with risk2:

        st.markdown(
            "### Interpretação"
        )

        st.write(
            risk_description(
                risk
            )
        )

        st.caption(
            "Quanto maior o índice, maior a volatilidade "
            "relativa considerada pelo modelo."
        )


    # ======================================================
    # ALERTAS
    # ======================================================

    st.divider()

    st.subheader(
        "⚠️ Alertas da Análise"
    )


    if not isinstance(
        alerts,
        list,
    ):

        alerts = [alerts]


    valid_alerts = [
        alert
        for alert in alerts
        if alert
    ]


    if valid_alerts:

        for alert in valid_alerts:

            if (
                "Nenhum alerta"
                in str(alert)
            ):

                st.success(
                    f"✅ {alert}"
                )

            else:

                st.warning(
                    f"⚠️ {alert}"
                )

    else:

        st.success(
            "✅ Nenhum alerta técnico relevante identificado."
        )


    # ======================================================
    # RESUMO EXECUTIVO
    # ======================================================

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


    # ======================================================
    # INDICADORES TÉCNICOS
    # ======================================================

    st.divider()

    st.subheader(
        "📈 Indicadores Técnicos"
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
    # SCORE EXPLICADO
    # ======================================================

    st.divider()

    st.subheader(
        "🧠 Composição do Score InvestIA"
    )


    st.caption(
        "O Score começa em 50 pontos e "
        "recebe ajustes conforme os indicadores."
    )


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


    bd1, bd2, bd3 = st.columns(
        3
    )


    # ======================================================
    # MA21
    # ======================================================

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


    # ======================================================
    # MA200
    # ======================================================

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


    # ======================================================
    # RSI
    # ======================================================

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
            f"| Cálculo bruto: {raw_score}"
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
            history,
            indicators,
        )


        if fig is not None:

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

        else:

            st.warning(
                "Não foi possível gerar o gráfico."
            )


    except Exception as error:

        st.warning(
            "O gráfico não pôde ser gerado."
        )

        st.exception(error)


    # ======================================================
    # ANÁLISE DETALHADA
    # ======================================================

    st.divider()

    st.subheader(
        "🔎 Análise Detalhada"
    )


    analysis_col1, analysis_col2 = st.columns(
        2
    )


    with analysis_col1:

        st.markdown(
            "### Fundamentação"
        )


        if reasons:

            for reason in reasons:

                st.write(
                    f"✔ {reason}"
                )

        else:

            st.info(
                "Nenhuma justificativa foi retornada."
            )


    with analysis_col2:

        st.markdown(
            "### 🛡️ Gestão de risco"
        )


        st.write(
            f"{risk_icon(risk)} **{risk}**"
        )


        st.write(
            f"**Índice de risco:** "
            f"{risk_points}/100"
        )


        st.write(
            f"**Score:** {score}/100"
        )


        st.write(
            f"**Tendência:** {trend}"
        )


        st.write(
            f"**RSI:** {rsi_status}"
        )


        st.write(
            f"**Sinal:** {qualified_signal}"
        )


        st.write(
            f"**Recomendação:** {recommendation}"
        )


    # ======================================================
    # RESUMO FINAL
    # ======================================================

    st.divider()

    st.subheader(
        "📋 Resumo da Análise"
    )


    summary1, summary2 = st.columns(
        2
    )


    with summary1:

        st.write(
            f"**Ativo:** {asset}"
        )


        st.write(
            f"**Preço:** "
            f"{format_currency(price)}"
        )


        st.write(
            f"**Score:** {score}/100"
        )


        st.write(
            f"**Classificação:** "
            f"{classification}"
        )


    with summary2:

        st.write(
            f"**Tendência:** {trend}"
        )


        st.write(
            f"**Sinal:** {qualified_signal}"
        )


        st.write(
            f"**Risco:** "
            f"{risk_icon(risk)} {risk}"
        )


        st.write(
            f"**Índice de risco:** "
            f"{risk_points}/100"
        )


        st.write(
            f"**Recomendação:** "
            f"{recommendation}"
        )


# ==========================================================
# TELA INICIAL
# ==========================================================

else:

    st.info(
        "Digite um ativo e clique em "
        "🔎 Analisar ativo."
    )


    st.markdown(
        """
### Como utilizar

1. Informe o código do ativo.
2. Escolha o período de análise.
3. Clique em **Analisar ativo**.
4. Consulte o Score InvestIA, tendência,
   risco, alertas e recomendação.

**Exemplos:** PETR4, VALE3, ITUB4.
"""
    )
