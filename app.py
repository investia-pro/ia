"""
InvestIA PRO
Aplicação principal

Versão: v0.6
Fase: 2.7.4 - Dashboard Executivo Consolidado
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
# FUNÇÕES AUXILIARES
# ==========================================================

def normalize_asset_input(asset):
    """
    Normaliza o código do ativo.
    """

    if asset is None:
        return ""

    return (
        str(asset)
        .strip()
        .upper()
        .replace(" ", "")
    )


def get_value(
    data,
    *keys,
    default=None,
):
    """
    Obtém um valor de um dicionário
    utilizando possíveis nomes alternativos.
    """

    if not isinstance(data, dict):
        return default

    for key in keys:

        if key in data:
            return data[key]

    return default


def safe_float(
    value,
    default=0.0,
):
    """
    Conversão segura para float.
    """

    try:
        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return default


def safe_int(
    value,
    default=0,
):
    """
    Conversão segura para inteiro.
    """

    try:
        return int(
            float(value)
        )

    except (
        TypeError,
        ValueError,
    ):
        return default


def get_risk_message(risk):
    """
    Mensagem operacional de risco.
    """

    messages = {

        "Baixo":
            "Baixa volatilidade relativa. "
            "O ativo apresenta menor oscilação "
            "dentro dos parâmetros analisados.",

        "Moderado":
            "Volatilidade intermediária. "
            "Recomenda-se acompanhamento antes "
            "de uma decisão operacional.",

        "Alto":
            "Volatilidade elevada. "
            "O ativo exige maior controle de risco "
            "e cautela na tomada de decisão.",
    }

    return messages.get(
        risk,
        "Nível de risco não identificado.",
    )


def get_signal_message(
    recommendation,
    risk,
):
    """
    Interpretação do sinal operacional.
    """

    if recommendation == "Compra":

        if risk == "Alto":

            return (
                "Cenário favorável, porém com "
                "risco elevado. A entrada exige cautela."
            )

        return (
            "Cenário técnico favorável "
            "ao movimento de alta."
        )


    if recommendation == "Compra Moderada":

        return (
            "Cenário parcialmente favorável. "
            "A confirmação dos indicadores "
            "é recomendável."
        )


    if recommendation == "Venda":

        if risk == "Alto":

            return (
                "Cenário desfavorável acompanhado "
                "de elevada volatilidade."
            )

        return (
            "Cenário técnico desfavorável "
            "ao movimento de alta."
        )


    if recommendation == "Venda Moderada":

        return (
            "Cenário parcialmente desfavorável. "
            "É necessária confirmação."
        )


    return (
        "Os indicadores não apresentam "
        "força suficiente para uma decisão."
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
# ENTRADA
# ==========================================================

input_col, period_col = st.columns(
    [3, 1]
)


with input_col:

    asset = st.text_input(
        "Digite o código do ativo",
        value="PETR4",
        max_chars=20,
    )


with period_col:

    period = st.selectbox(
        "Período",
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
# PROCESSAMENTO
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
    # MERCADO
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

            st.exception(
                error
            )

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

        st.exception(
            error
        )

        st.stop()


    if prepared_data is None:

        st.error(
            "Os dados do mercado não puderam ser preparados."
        )

        st.stop()


    # ======================================================
    # HISTÓRICO
    # ======================================================

    history = None


    if isinstance(
        prepared_data,
        dict,
    ):

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

    price = None


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
    # DADOS PARA ANÁLISE
    # ======================================================

    analysis_data = {

        "price":
            price,

        "rsi":
            get_value(
                indicators,
                "rsi",
            ),

        "ma21":
            get_value(
                indicators,
                "ma21",
            ),

        "ma200":
            get_value(
                indicators,
                "ma200",
            ),

        "volatility":
            get_value(
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
    # ANÁLISE INVESTIA
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

                st.exception(
                    error
                )

                st.stop()

        except Exception as error:

            st.error(
                "Erro ao executar a análise InvestIA."
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

    score = safe_int(
        get_value(
            result,
            "score",
            default=0,
        )
    )


    classification = get_value(
        result,
        "classification",
        default="NEUTRO",
    )


    signal = get_value(
        result,
        "signal",
        default="NEUTRO",
    )


    qualified_signal = get_value(
        result,
        "qualified_signal",
        default=signal,
    )


    signal_level = get_value(
        result,
        "signal_level",
        default="Neutro",
    )


    signal_icon = get_value(
        result,
        "signal_icon",
        default="🟡",
    )


    trend = get_value(
        result,
        "trend",
        "tendencia",
        default="Neutra",
    )


    recommendation = get_value(
        result,
        "recommendation",
        "recomendacao",
        default="Aguardar",
    )


    risk = get_value(
        result,
        "risk",
        "risco",
        default="Moderado",
    )


    risk_score = safe_int(
        get_value(
            result,
            "risk_score",
            default=0,
        )
    )


    rsi_status = get_value(
        result,
        "rsi_status",
        default="Neutro",
    )


    reasons = get_value(
        result,
        "reasons",
        "justificativas",
        default=[],
    )


    alerts = get_value(
        result,
        "alerts",
        default=[],
    )


    breakdown = get_value(
        result,
        "breakdown",
        default={},
    )


    executive_summary = get_value(
        result,
        "executive_summary",
        default="",
    )


    # ======================================================
    # DASHBOARD
    # ======================================================

    st.divider()

    st.header(
        f"📊 Dashboard Executivo — {asset}"
    )


    # ======================================================
    # PAINEL PRINCIPAL
    # ======================================================

    st.subheader(
        "🎯 Visão Geral"
    )


    main1, main2, main3, main4, main5 = st.columns(
        5
    )


    with main1:

        st.metric(
            "Preço",
            format_currency(
                price
            ),
        )


    with main2:

        st.metric(
            "Score",
            f"{score}/100",
        )


    with main3:

        st.metric(
            "Tendência",
            str(trend),
        )


    with main4:

        st.metric(
            "Risco",
            f"{risk_icon(risk)} {risk}",
        )


    with main5:

        st.metric(
            "Recomendação",
            str(recommendation),
        )


    # ======================================================
    # SINAL
    # ======================================================

    st.divider()

    signal_col1, signal_col2 = st.columns(
        [2, 1]
    )


    with signal_col1:

        st.subheader(
            "🎯 Sinal InvestIA"
        )

        st.markdown(
            f"# {signal_icon} {qualified_signal}"
        )

        st.write(
            get_signal_message(
                recommendation,
                risk,
            )
        )


    with signal_col2:

        st.subheader(
            "Nível do sinal"
        )

        st.metric(
            "Confiança operacional",
            str(signal_level),
        )

        st.caption(
            f"Sinal base: {signal}"
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
    # RISCO
    # ======================================================

    st.divider()

    st.subheader(
        "🛡️ Gestão de Risco"
    )


    risk_col1, risk_col2, risk_col3 = st.columns(
        3
    )


    with risk_col1:

        st.metric(
            "Nível de risco",
            f"{risk_icon(risk)} {risk}",
        )


    with risk_col2:

        st.metric(
            "Índice de risco",
            f"{risk_score}/100",
        )


    with risk_col3:

        st.metric(
            "RSI",
            f'{safe_float(analysis_data["rsi"]):.2f}',
        )


    st.info(
        get_risk_message(
            risk
        )
    )


    # ======================================================
    # ALERTAS
    # ======================================================

    st.divider()

    st.subheader(
        "⚠️ Alertas Técnicos"
    )


    if not isinstance(
        alerts,
        list,
    ):

        alerts = [alerts]


    alerts = [
        alert
        for alert in alerts
        if alert
    ]


    if alerts:

        for alert in alerts:

            if "Nenhum alerta" in str(alert):

                st.success(
                    f"✅ {alert}"
                )

            else:

                st.warning(
                    f"⚠️ {alert}"
                )

    else:

        st.success(
            "✅ Nenhum alerta técnico relevante."
        )


    # ======================================================
    # INDICADORES
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
            f'{safe_float(analysis_data["rsi"]):.2f}',
        )


    with ind4:

        volatility_percent = (
            safe_float(
                analysis_data["volatility"]
            )
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
        "📊 Evolução do Preço"
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

        st.exception(
            error
        )


    # ======================================================
    # COMPOSIÇÃO DO SCORE
    # ======================================================

    st.divider()

    st.subheader(
        "🧠 Composição do Score InvestIA"
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


    score1, score2, score3 = st.columns(
        3
    )


    # ------------------------------------------------------
    # MA21
    # ------------------------------------------------------

    with score1:

        ma21_data = {}


        if isinstance(
            breakdown,
            dict,
        ):

            ma21_data = breakdown.get(
                "ma21",
                {},
            )


        st.markdown(
            "### 📏 MA21"
        )


        st.metric(
            "Contribuição",
            f'{ma21_data.get("points", 0):+d} pts',
        )


        st.write(
            f'**Sinal:** '
            f'{ma21_data.get("signal", "Neutro")}'
        )


        st.caption(
            ma21_data.get(
                "reason",
                "Sem informação.",
            )
        )


    # ------------------------------------------------------
    # MA200
    # ------------------------------------------------------

    with score2:

        ma200_data = {}


        if isinstance(
            breakdown,
            dict,
        ):

            ma200_data = breakdown.get(
                "ma200",
                {},
            )


        st.markdown(
            "### 📐 MA200"
        )


        st.metric(
            "Contribuição",
            f'{ma200_data.get("points", 0):+d} pts',
        )


        st.write(
            f'**Sinal:** '
            f'{ma200_data.get("signal", "Neutro")}'
        )


        st.caption(
            ma200_data.get(
                "reason",
                "Sem informação.",
            )
        )


    # ------------------------------------------------------
    # RSI
    # ------------------------------------------------------

    with score3:

        rsi_data = {}


        if isinstance(
            breakdown,
            dict,
        ):

            rsi_data = breakdown.get(
                "rsi",
                {},
            )


        st.markdown(
            "### 📊 RSI"
        )


        st.metric(
            "Contribuição",
            f'{rsi_data.get("points", 0):+d} pts',
        )


        st.write(
            f'**Sinal:** '
            f'{rsi_data.get("signal", "Neutro")}'
        )


        st.caption(
            rsi_data.get(
                "reason",
                "Sem informação.",
            )
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
            f"**Score InvestIA: {score}/100** "
            f"| Cálculo bruto: {raw_score}"
        )

    else:

        st.success(
            f"**Score InvestIA: {score}/100**"
        )


    # ======================================================
    # ANÁLISE DETALHADA
    # ======================================================

    st.divider()

    st.subheader(
        "🔎 Análise Detalhada"
    )


    detail1, detail2 = st.columns(
        2
    )


    with detail1:

        st.markdown(
            "### Fundamentação"
        )


        if reasons:

            if not isinstance(
                reasons,
                list,
            ):

                reasons = [reasons]


            for reason in reasons:

                st.write(
                    f"✔ {reason}"
                )

        else:

            st.info(
                "Nenhuma justificativa foi retornada."
            )


    with detail2:

        st.markdown(
            "### Situação Técnica"
        )


        st.write(
            f"**Classificação:** {classification}"
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
            f"**Risco:** "
            f"{risk_icon(risk)} {risk}"
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
            f"**Classificação:** {classification}"
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
            f"**Recomendação:** {recommendation}"
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
4. Consulte o Score, tendência, risco,
   alertas e recomendação.

**Exemplos:** PETR4, VALE3, ITUB4.
"""
    )
