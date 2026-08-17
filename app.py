"""
InvestIA PRO
Aplicação principal

Versão: v0.6
Fase: 2.8.4 - Consolidação do Dashboard Executivo
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

    if not isinstance(
        indicators,
        dict,
    ):
        return default

    value = indicators.get(
        key,
        default,
    )

    return value


def get_analysis_value(
    result,
    *keys,
    default=None,
):
    """
    Obtém valores da análise aceitando
    nomes alternativos.
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


def safe_number(
    value,
    default=0.0,
):
    """
    Converte valores numéricos com segurança.
    """

    try:

        if value is None:
            return default

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return default


def format_score(value):
    """
    Formata o Score de maneira segura.
    """

    value = safe_number(
        value,
        0,
    )

    return f"{int(round(value))}/100"


def format_rsi(value):
    """
    Formata RSI.
    """

    value = safe_number(
        value,
        0,
    )

    return f"{value:.2f}"


def format_volatility(value):
    """
    Converte volatilidade decimal para percentual.
    """

    value = safe_number(
        value,
        0,
    )

    return f"{value * 100:.2f}%"


# ==========================================================
# ENTRADA DO USUÁRIO
# ==========================================================

col_input, col_period = st.columns(
    [3, 1]
)


with col_input:

    asset_input = st.text_input(
        "Digite o código do ativo",
        value="PETR4",
        max_chars=20,
        placeholder="Ex.: PETR4, VALE3, ITUB4",
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

    # ======================================================
    # NORMALIZAÇÃO
    # ======================================================

    asset = normalize_asset_input(
        asset_input
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
        f"Buscando dados de {asset}..."
    ):

        try:

            market_data = get_market_data(
                asset,
                period,
            )

        except Exception as error:

            st.error(
                "Não foi possível consultar "
                "os dados do mercado."
            )

            st.caption(
                "Verifique se o ativo existe ou "
                "tente novamente em alguns instantes."
            )

            with st.expander(
                "Detalhes técnicos"
            ):

                st.exception(
                    error
                )

            st.stop()

    # ======================================================
    # VALIDAÇÃO DO RETORNO DO MARKET
    # ======================================================

    if market_data is None:

        st.error(
            f"Não foi possível obter dados para {asset}."
        )

        st.stop()

    # ======================================================
    # PREPARAÇÃO DOS DADOS
    # ======================================================

    with st.spinner(
        "Preparando dados do mercado..."
    ):

        try:

            prepared_data = prepare_market_data(
                market_data
            )

        except Exception as error:

            st.error(
                "Erro ao preparar os dados "
                "do mercado."
            )

            with st.expander(
                "Detalhes técnicos"
            ):

                st.exception(
                    error
                )

            st.stop()

    # ======================================================
    # VALIDAÇÃO DA PREPARAÇÃO
    # ======================================================

    if prepared_data is None:

        st.error(
            "Os dados do mercado não puderam "
            "ser preparados."
        )

        st.stop()

    if not isinstance(
        prepared_data,
        dict,
    ):

        st.error(
            "O módulo de mercado retornou "
            "um formato de dados inválido."
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
            "O histórico do ativo não foi encontrado."
        )

        st.stop()

    try:

        if history.empty:

            st.error(
                "O histórico do ativo está vazio."
            )

            st.stop()

    except AttributeError:

        st.error(
            "O histórico retornado possui "
            "um formato inválido."
        )

        st.stop()

    # ======================================================
    # PREÇO ATUAL
    # ======================================================

    with st.spinner(
        "Obtendo preço atual..."
    ):

        try:

            price = get_current_price(
                prepared_data
            )

        except Exception as error:

            st.error(
                "Não foi possível determinar "
                "o preço atual."
            )

            with st.expander(
                "Detalhes técnicos"
            ):

                st.exception(
                    error
                )

            st.stop()

    if price is None:

        st.error(
            "O preço atual não está disponível."
        )

        st.stop()

    price = safe_number(
        price,
        None,
    )

    if price is None:

        st.error(
            "O preço atual possui "
            "um formato inválido."
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
                "Erro ao calcular os "
                "indicadores técnicos."
            )

            with st.expander(
                "Detalhes técnicos"
            ):

                st.exception(
                    error
                )

            st.stop()

    if indicators is None:

        st.error(
            "Os indicadores não foram calculados."
        )

        st.stop()

    if not isinstance(
        indicators,
        dict,
    ):

        st.error(
            "O módulo de indicadores retornou "
            "um formato inválido."
        )

        st.stop()

    # ======================================================
    # EXTRAÇÃO DOS INDICADORES
    # ======================================================

    rsi = get_indicator_value(
        indicators,
        "rsi",
    )

    ma21 = get_indicator_value(
        indicators,
        "ma21",
    )

    ma200 = get_indicator_value(
        indicators,
        "ma200",
    )

    volatility = get_indicator_value(
        indicators,
        "volatility",
        default=0,
    )

    # ======================================================
    # DADOS PARA ANÁLISE
    # ======================================================

    analysis_data = {

        "price":
            price,

        "rsi":
            rsi,

        "ma21":
            ma21,

        "ma200":
            ma200,

        "volatility":
            volatility,

    }

    # ======================================================
    # VALIDAÇÃO DOS INDICADORES
    # ======================================================

    if not validate_analysis_data(
        analysis_data
    ):

        st.error(
            "Os dados técnicos são insuficientes "
            "para realizar a análise."
        )

        st.write(
            "Indicadores recebidos:"
        )

        st.json(
            {
                "price": price,
                "rsi": rsi,
                "ma21": ma21,
                "ma200": ma200,
                "volatility": volatility,
            }
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

        except Exception as error:

            st.error(
                "Erro ao executar a análise InvestIA."
            )

            with st.expander(
                "Detalhes técnicos"
            ):

                st.exception(
                    error
                )

            st.stop()

    # ======================================================
    # VALIDAÇÃO DO RESULTADO
    # ======================================================

    if result is None:

        st.error(
            "A análise não retornou resultado."
        )

        st.stop()

    if not isinstance(
        result,
        dict,
    ):

        st.error(
            "O motor de análise retornou "
            "um formato inválido."
        )

        st.stop()

    # ======================================================
    # RESULTADOS PRINCIPAIS
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
        default="Aguardar",
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
    # DASHBOARD
    # ======================================================

    st.divider()

    st.header(
        f"📊 Análise do ativo: {asset}"
    )

    st.caption(
        f"Período analisado: {period}"
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
            format_score(
                score
            ),
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
        f"**Classificação:** {classification} "
        f"| **Sinal:** {qualified_signal} "
        f"| **Nível:** "
        f"{signal_icon} {signal_level}"
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
                ma21
            ),
        )

    with ind2:

        st.metric(
            "MA200",
            format_currency(
                ma200
            ),
        )

    with ind3:

        st.metric(
            "RSI",
            format_rsi(
                rsi
            ),
        )

    with ind4:

        st.metric(
            "Volatilidade",
            format_volatility(
                volatility
            ),
        )

    # ======================================================
    # SCORE EXPLICADO
    # ======================================================

    st.divider()

    st.subheader(
        "🧠 Composição do Score InvestIA"
    )

    st.caption(
        "O Score começa em 50 pontos e recebe "
        "ajustes conforme os indicadores técnicos."
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
        f"**Base:** {int(base_points):+d} pontos"
    )

    # ======================================================
    # COMPONENTES DO SCORE
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

        if not isinstance(
            ma21_data,
            dict,
        ):

            ma21_data = {}

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
            f"{int(ma21_points):+d} pts",
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

        if not isinstance(
            ma200_data,
            dict,
        ):

            ma200_data = {}

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
            f"{int(ma200_points):+d} pts",
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

        if not isinstance(
            rsi_data,
            dict,
        ):

            rsi_data = {}

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
            f"{int(rsi_points):+d} pts",
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
            f"**Score final: {format_score(score)}** "
            f"| Cálculo bruto: {raw_score}"
        )

    else:

        st.success(
            f"**Score final: {format_score(score)}**"
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
                "Não foi possível gerar o gráfico "
                "com o histórico disponível."
            )

    except Exception as error:

        st.warning(
            "O gráfico não pôde ser gerado, "
            "mas a análise continua disponível."
        )

        with st.expander(
            "Detalhes técnicos do gráfico"
        ):

            st.exception(
                error
            )

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

    # ------------------------------------------------------
    # FUNDAMENTAÇÃO
    # ------------------------------------------------------

    with analysis_col1:

        st.markdown(
            "### Fundamentação"
        )

        if isinstance(
            reasons,
            (list, tuple),
        ) and reasons:

            for reason in reasons:

                st.write(
                    f"✔ {reason}"
                )

        elif reasons:

            st.write(
                str(reasons)
            )

        else:

            st.info(
                "Nenhuma justificativa "
                "foi retornada."
            )

    # ------------------------------------------------------
    # GESTÃO DE RISCO
    # ------------------------------------------------------

    with analysis_col2:

        st.markdown(
            "### 🛡️ Gestão de risco"
        )

        st.write(
            f"{risk_icon(risk)} **{risk}**"
        )

        st.write(
            f"**Score:** {format_score(score)}"
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
            f"**Score:** "
            f"{format_score(score)}"
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
            f"**Recomendação:** "
            f"{recommendation}"
        )

    # ======================================================
    # INFORMAÇÕES TÉCNICAS
    # ======================================================

    with st.expander(
        "🔧 Informações técnicas"
    ):

        st.write(
            f"**Ativo:** {asset}"
        )

        st.write(
            f"**Período:** {period}"
        )

        st.write(
            f"**Preço:** {price}"
        )

        st.write(
            f"**MA21:** {ma21}"
        )

        st.write(
            f"**MA200:** {ma200}"
        )

        st.write(
            f"**RSI:** {rsi}"
        )

        st.write(
            f"**Volatilidade:** {volatility}"
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
   risco e recomendação.

### Exemplos

`PETR4` · `VALE3` · `ITUB4`

---

### 📊 O que o Dashboard apresenta

- Preço atual
- Score InvestIA
- Classificação
- Tendência
- Sinal operacional
- Recomendação
- Nível de risco
- RSI
- MA21
- MA200
- Volatilidade
- Composição do Score
- Justificativas da análise
- Evolução histórica do preço
"""
    )
