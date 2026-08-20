"""
InvestIA PRO
Aplicação principal

Versão: v0.7
Fase: 3.0.3 - Dashboard de Score Integrado
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

st.title(
    "📈 InvestIA PRO"
)

st.caption(
    "Análise técnica, fundamentalista e integrada de ativos financeiros"
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
    Obtém valores do resultado da análise
    aceitando nomes alternativos.
    """

    if not isinstance(
        result,
        dict,
    ):
        return default

    for key in keys:

        if key in result:

            value = result.get(
                key
            )

            if value is not None:
                return value

    return default


def safe_number(
    value,
    default=None,
):
    """
    Converte um valor para float com segurança.
    """

    try:

        if value is None:
            return default

        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return default


def format_percent(
    value,
    decimals=2,
):
    """
    Formata valores percentuais.
    """

    value = safe_number(
        value
    )

    if value is None:
        return "N/D"

    return (
        f"{value:.{decimals}f}%"
    )


def format_weight(
    value,
):
    """
    Formata pesos da composição do Score.
    """

    value = safe_number(
        value,
        default=0,
    )

    return (
        f"{value * 100:.0f}%"
    )


def score_delta(
    score,
):
    """
    Retorna o delta visual em relação
    ao ponto neutro do Score.
    """

    score = safe_number(
        score
    )

    if score is None:
        return None

    delta = score - 50

    if delta > 0:
        return f"+{delta:.0f} vs neutro"

    if delta < 0:
        return f"{delta:.0f} vs neutro"

    return "Neutro"


# ==========================================================
# ENTRADA DO USUÁRIO
# ==========================================================

input_col, period_col = st.columns(
    [3, 1]
)


with input_col:

    asset = st.text_input(
        "Digite o código do ativo",
        value="PETR4",
        max_chars=20,
        placeholder="Ex.: PETR4, VALE3, ITUB4",
    )


with period_col:

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
# EXECUÇÃO DA ANÁLISE
# ==========================================================

if analyze_button:

    asset = normalize_asset_input(
        asset
    )

    # ======================================================
    # VALIDAÇÃO DO ATIVO
    # ======================================================

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

    # ======================================================
    # VALIDAÇÃO DOS DADOS
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
        "Preparando dados para análise..."
    ):

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

    if not isinstance(
        prepared_data,
        dict,
    ):

        st.error(
            "Formato inválido dos dados preparados."
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

    if getattr(
        history,
        "empty",
        True,
    ):

        st.error(
            "O histórico do ativo está vazio."
        )

        st.stop()

    # ======================================================
    # PREÇO ATUAL
    # ======================================================

    try:

        price = get_current_price(
            prepared_data
        )

    except Exception:

        price = prepared_data.get(
            "price"
        )

    price = safe_number(
        price
    )

    if price is None:

        st.error(
            "Não foi possível determinar o preço atual."
        )

        st.stop()

    # ======================================================
    # INDICADORES TÉCNICOS
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

    if not isinstance(
        indicators,
        dict,
    ):

        st.error(
            "Os indicadores não foram calculados corretamente."
        )

        st.stop()

    # ======================================================
    # FUNDAMENTOS
    # ======================================================

    fundamentals = prepared_data.get(
        "fundamentals",
        {}
    )

    if not isinstance(
        fundamentals,
        dict,
    ):

        fundamentals = {}

    # ======================================================
    # DADOS PARA O MOTOR DE ANÁLISE
    # ======================================================

    analysis_data = {

        "price":
            price,

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

        "rsi":
            get_indicator_value(
                indicators,
                "rsi",
            ),

        "volatility":
            get_indicator_value(
                indicators,
                "volatility",
            ),

        "fundamentals":
            fundamentals,
    }

    # ======================================================
    # VALIDAÇÃO DOS DADOS TÉCNICOS
    # ======================================================

    technical_validation_data = {

        "price":
            analysis_data.get(
                "price"
            ),

        "ma21":
            analysis_data.get(
                "ma21"
            ),

        "ma200":
            analysis_data.get(
                "ma200"
            ),

        "rsi":
            analysis_data.get(
                "rsi"
            ),

        "volatility":
            analysis_data.get(
                "volatility"
            ),
    }

    if not validate_analysis_data(
        technical_validation_data
    ):

        st.error(
            "Os dados técnicos são insuficientes "
            "para realizar a análise."
        )

        st.write(
            {
                "price":
                    analysis_data.get("price"),

                "ma21":
                    analysis_data.get("ma21"),

                "ma200":
                    analysis_data.get("ma200"),

                "rsi":
                    analysis_data.get("rsi"),

                "volatility":
                    analysis_data.get("volatility"),
            }
        )

        st.stop()

    # ======================================================
    # MOTOR DE ANÁLISE INTEGRADA
    # ======================================================

    with st.spinner(
        "Executando análise integrada InvestIA..."
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

            st.exception(
                error
            )

            st.stop()

    # ======================================================
    # VALIDAÇÃO DO RESULTADO
    # ======================================================

    if not isinstance(
        result,
        dict,
    ):

        st.error(
            "A análise não retornou um resultado válido."
        )

        st.stop()

    # ======================================================
    # EXTRAÇÃO DOS RESULTADOS PRINCIPAIS
    # ======================================================

    score = get_analysis_value(
        result,
        "integrated_score",
        "score",
        default=0,
    )

    classification = get_analysis_value(
        result,
        "integrated_classification",
        "classification",
        default="NEUTRO",
    )

    signal = get_analysis_value(
        result,
        "integrated_signal",
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

    executive_summary = get_analysis_value(
        result,
        "executive_summary",
        default="",
    )

    # ======================================================
    # SCORES INDIVIDUAIS
    # ======================================================

    technical_score = get_analysis_value(
        result,
        "technical_score",
        default=None,
    )

    fundamental_score = get_analysis_value(
        result,
        "fundamental_score",
        default=None,
    )

    integrated_score = get_analysis_value(
        result,
        "integrated_score",
        "score",
        default=score,
    )

    technical_classification = get_analysis_value(
        result,
        "technical_classification",
        default="N/D",
    )

    fundamental_classification = get_analysis_value(
        result,
        "fundamental_classification",
        default="Indisponível",
    )

    integrated_classification = get_analysis_value(
        result,
        "integrated_classification",
        "classification",
        default=classification,
    )

    technical_signal = get_analysis_value(
        result,
        "technical_signal",
        default="N/D",
    )

    fundamental_signal = get_analysis_value(
        result,
        "fundamental_signal",
        default="Indisponível",
    )

    integrated_signal = get_analysis_value(
        result,
        "integrated_signal",
        "signal",
        default=signal,
    )

    fundamental_status = get_analysis_value(
        result,
        "fundamental_status",
        default="Indisponível",
    )

    fundamental_completeness = get_analysis_value(
        result,
        "fundamental_completeness",
        default=0,
    )

    # ======================================================
    # BREAKDOWNS
    # ======================================================

    technical_breakdown = get_analysis_value(
        result,
        "technical_breakdown",
        "breakdown",
        default={},
    )

    fundamental_breakdown = get_analysis_value(
        result,
        "fundamental_breakdown",
        default={},
    )

    integrated_breakdown = get_analysis_value(
        result,
        "integrated_breakdown",
        default={},
    )

    if not isinstance(
        technical_breakdown,
        dict,
    ):

        technical_breakdown = {}

    if not isinstance(
        fundamental_breakdown,
        dict,
    ):

        fundamental_breakdown = {}

    if not isinstance(
        integrated_breakdown,
        dict,
    ):

        integrated_breakdown = {}

    # ======================================================
    # PESOS
    # ======================================================

    technical_weight = 1.0

    fundamental_weight = 0.0

    score_method = "Técnico"

    integrated_info = integrated_breakdown.get(
        "integrated",
        {}
    )

    technical_info = integrated_breakdown.get(
        "technical",
        {}
    )

    fundamental_info = integrated_breakdown.get(
        "fundamental",
        {}
    )

    if isinstance(
        technical_info,
        dict,
    ):

        technical_weight = safe_number(
            technical_info.get(
                "weight"
            ),
            default=technical_weight,
        )

    if isinstance(
        fundamental_info,
        dict,
    ):

        fundamental_weight = safe_number(
            fundamental_info.get(
                "weight"
            ),
            default=fundamental_weight,
        )

    if isinstance(
        integrated_info,
        dict,
    ):

        score_method = integrated_info.get(
            "method",
            score_method,
        )

    # ======================================================
    # CABEÇALHO DA ANÁLISE
    # ======================================================

    st.divider()

    st.header(
        f"📊 Análise Integrada: {asset}"
    )

    # ======================================================
    # MÉTRICAS PRINCIPAIS
    # ======================================================

    main1, main2, main3, main4 = st.columns(
        4
    )

    with main1:

        st.metric(
            "Preço Atual",
            format_currency(
                price
            ),
        )

    with main2:

        st.metric(
            "Score Integrado",
            f"{integrated_score}/100",
            score_delta(
                integrated_score
            ),
        )

    with main3:

        st.metric(
            "Tendência",
            str(
                trend
            ),
        )

    with main4:

        st.metric(
            "Recomendação",
            str(
                recommendation
            ),
        )

    # ======================================================
    # STATUS GERAL
    # ======================================================

    st.info(
        f"**Classificação:** {integrated_classification} "
        f"| **Sinal:** {qualified_signal} "
        f"| **Nível:** {signal_icon} {signal_level}"
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
    # TRÊS SCORES
    # ======================================================

    st.divider()

    st.subheader(
        "🧠 Score InvestIA"
    )

    st.caption(
        "Visão separada da análise técnica, fundamentalista e integrada."
    )

    score_col1, score_col2, score_col3 = st.columns(
        3
    )

    # ------------------------------------------------------
    # SCORE TÉCNICO
    # ------------------------------------------------------

    with score_col1:

        st.markdown(
            "### 📈 Score Técnico"
        )

        if technical_score is not None:

            st.metric(
                "Score",
                f"{technical_score}/100",
                score_delta(
                    technical_score
                ),
            )

            st.write(
                f"**Classificação:** "
                f"{technical_classification}"
            )

            st.write(
                f"**Sinal:** "
                f"{technical_signal}"
            )

            st.caption(
                f"Peso no Score Integrado: "
                f"{format_weight(technical_weight)}"
            )

        else:

            st.warning(
                "Score técnico indisponível."
            )

    # ------------------------------------------------------
    # SCORE FUNDAMENTALISTA
    # ------------------------------------------------------

    with score_col2:

        st.markdown(
            "### 🏢 Score Fundamentalista"
        )

        if fundamental_score is not None:

            st.metric(
                "Score",
                f"{fundamental_score}/100",
                score_delta(
                    fundamental_score
                ),
            )

            st.write(
                f"**Classificação:** "
                f"{fundamental_classification}"
            )

            st.write(
                f"**Sinal:** "
                f"{fundamental_signal}"
            )

            st.caption(
                f"Peso no Score Integrado: "
                f"{format_weight(fundamental_weight)}"
            )

        else:

            st.metric(
                "Score",
                "N/D",
            )

            st.write(
                f"**Status:** "
                f"{fundamental_status}"
            )

            st.caption(
                "Dados fundamentalistas indisponíveis."
            )

    # ------------------------------------------------------
    # SCORE INTEGRADO
    # ------------------------------------------------------

    with score_col3:

        st.markdown(
            "### ⭐ Score Integrado"
        )

        st.metric(
            "Score Final",
            f"{integrated_score}/100",
            score_delta(
                integrated_score
            ),
        )

        st.write(
            f"**Classificação:** "
            f"{integrated_classification}"
        )

        st.write(
            f"**Sinal:** "
            f"{integrated_signal}"
        )

        st.caption(
            f"Método: {score_method}"
        )

    # ======================================================
    # COMPOSIÇÃO DO SCORE INTEGRADO
    # ======================================================

    st.divider()

    st.subheader(
        "⚖️ Composição do Score Integrado"
    )

    composition1, composition2, composition3 = st.columns(
        3
    )

    with composition1:

        st.metric(
            "Peso Técnico",
            format_weight(
                technical_weight
            ),
        )

    with composition2:

        st.metric(
            "Peso Fundamentalista",
            format_weight(
                fundamental_weight
            ),
        )

    with composition3:

        completeness_value = safe_number(
            fundamental_completeness,
            default=0,
        )

        st.metric(
            "Cobertura Fundamentalista",
            f"{completeness_value * 100:.0f}%",
        )

    st.caption(
        f"Status dos fundamentos: **{fundamental_status}** "
        f"| Método utilizado: **{score_method}**"
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
                analysis_data.get(
                    "ma21"
                )
            ),
        )

    with ind2:

        st.metric(
            "MA200",
            format_currency(
                analysis_data.get(
                    "ma200"
                )
            ),
        )

    with ind3:

        rsi_value = safe_number(
            analysis_data.get(
                "rsi"
            )
        )

        st.metric(
            "RSI",
            (
                f"{rsi_value:.2f}"
                if rsi_value is not None
                else "N/D"
            ),
        )

        st.caption(
            rsi_status
        )

    with ind4:

        volatility = safe_number(
            analysis_data.get(
                "volatility"
            )
        )

        if volatility is not None:

            volatility_percent = (
                volatility
                * 100
            )

            st.metric(
                "Volatilidade",
                f"{volatility_percent:.2f}%",
            )

        else:

            st.metric(
                "Volatilidade",
                "N/D",
            )

    # ======================================================
    # DETALHAMENTO DO SCORE TÉCNICO
    # ======================================================

    st.divider()

    st.subheader(
        "📐 Composição do Score Técnico"
    )

    technical_base = technical_breakdown.get(
        "base",
        50,
    )

    st.caption(
        f"Score base: {technical_base} pontos"
    )

    tech1, tech2, tech3 = st.columns(
        3
    )

    technical_items = [

        (
            tech1,
            "📏 MA21",
            "ma21",
        ),

        (
            tech2,
            "📐 MA200",
            "ma200",
        ),

        (
            tech3,
            "📊 RSI",
            "rsi",
        ),
    ]

    for column, title, key in technical_items:

        with column:

            item = technical_breakdown.get(
                key,
                {}
            )

            if not isinstance(
                item,
                dict,
            ):

                item = {}

            points = item.get(
                "points",
                0,
            )

            item_signal = item.get(
                "signal",
                "Neutro",
            )

            reason = item.get(
                "reason",
                "Sem informação.",
            )

            st.markdown(
                f"### {title}"
            )

            st.metric(
                "Contribuição",
                f"{points:+d} pts",
            )

            st.write(
                f"**Sinal:** {item_signal}"
            )

            st.caption(
                reason
            )

    technical_raw_score = technical_breakdown.get(
        "raw_score"
    )

    if technical_raw_score is not None:

        st.success(
            f"**Score Técnico Final: {technical_score}/100** "
            f"| Score bruto: {technical_raw_score}"
        )

    # ======================================================
    # DETALHAMENTO DO SCORE FUNDAMENTALISTA
    # ======================================================

    st.divider()

    st.subheader(
        "🏢 Análise Fundamentalista"
    )

    if fundamental_score is None:

        st.warning(
            "Os dados fundamentalistas necessários "
            "para calcular o Score Fundamentalista "
            "ainda não estão disponíveis para este ativo."
        )

    else:

        fund1, fund2, fund3 = st.columns(
            3
        )

        fund_items = [

            (
                fund1,
                "P/L",
                "pe_ratio",
            ),

            (
                fund2,
                "P/VP",
                "price_to_book",
            ),

            (
                fund3,
                "Dividend Yield",
                "dividend_yield",
            ),
        ]

        for column, label, key in fund_items:

            with column:

                item = fundamental_breakdown.get(
                    key,
                    {}
                )

                if not isinstance(
                    item,
                    dict,
                ):

                    item = {}

                points = item.get(
                    "points",
                    0,
                )

                item_signal = item.get(
                    "signal",
                    "N/D",
                )

                reason = item.get(
                    "reason",
                    "Sem informação.",
                )

                st.markdown(
                    f"### {label}"
                )

                st.metric(
                    "Contribuição",
                    f"{points:+d} pts",
                )

                st.write(
                    f"**Sinal:** {item_signal}"
                )

                st.caption(
                    reason
                )

        fund4, fund5, fund6 = st.columns(
            3
        )

        fund_items_2 = [

            (
                fund4,
                "ROE",
                "roe",
            ),

            (
                fund5,
                "Margem de Lucro",
                "profit_margin",
            ),

            (
                fund6,
                "Dívida/Patrimônio",
                "debt_to_equity",
            ),
        ]

        for column, label, key in fund_items_2:

            with column:

                item = fundamental_breakdown.get(
                    key,
                    {}
                )

                if not isinstance(
                    item,
                    dict,
                ):

                    item = {}

                points = item.get(
                    "points",
                    0,
                )

                item_signal = item.get(
                    "signal",
                    "N/D",
                )

                reason = item.get(
                    "reason",
                    "Sem informação.",
                )

                st.markdown(
                    f"### {label}"
                )

                st.metric(
                    "Contribuição",
                    f"{points:+d} pts",
                )

                st.write(
                    f"**Sinal:** {item_signal}"
                )

                st.caption(
                    reason
                )

        fundamental_raw_score = fundamental_breakdown.get(
            "raw_score"
        )

        if fundamental_raw_score is not None:

            st.success(
                f"**Score Fundamentalista Final: "
                f"{fundamental_score}/100** "
                f"| Score bruto: "
                f"{fundamental_raw_score}"
            )

        else:

            st.success(
                f"**Score Fundamentalista Final: "
                f"{fundamental_score}/100**"
            )

    # ======================================================
    # DADOS FUNDAMENTALISTAS DISPONÍVEIS
    # ======================================================

    st.divider()

    st.subheader(
        "📋 Dados Fundamentalistas"
    )

    fund_data1, fund_data2, fund_data3 = st.columns(
        3
    )

    with fund_data1:

        st.write(
            f"**Empresa:** "
            f"{fundamentals.get('company_name') or 'N/D'}"
        )

        st.write(
            f"**Setor:** "
            f"{fundamentals.get('sector') or 'N/D'}"
        )

        st.write(
            f"**Indústria:** "
            f"{fundamentals.get('industry') or 'N/D'}"
        )

    with fund_data2:

        pe_ratio = safe_number(
            fundamentals.get(
                "pe_ratio"
            )
        )

        price_to_book = safe_number(
            fundamentals.get(
                "price_to_book"
            )
        )

        dividend_yield = safe_number(
            fundamentals.get(
                "dividend_yield"
            )
        )

        st.write(
            f"**P/L:** "
            f"{pe_ratio:.2f}"
            if pe_ratio is not None
            else "**P/L:** N/D"
        )

        st.write(
            f"**P/VP:** "
            f"{price_to_book:.2f}"
            if price_to_book is not None
            else "**P/VP:** N/D"
        )

        st.write(
            f"**Dividend Yield:** "
            f"{format_percent(dividend_yield)}"
        )

    with fund_data3:

        roe = safe_number(
            fundamentals.get(
                "roe"
            )
        )

        profit_margin = safe_number(
            fundamentals.get(
                "profit_margin"
            )
        )

        debt_to_equity = safe_number(
            fundamentals.get(
                "debt_to_equity"
            )
        )

        st.write(
            f"**ROE:** "
            f"{format_percent(roe)}"
        )

        st.write(
            f"**Margem de Lucro:** "
            f"{format_percent(profit_margin)}"
        )

        st.write(
            f"**Dívida/Patrimônio:** "
            f"{debt_to_equity:.2f}"
            if debt_to_equity is not None
            else "**Dívida/Patrimônio:** N/D"
        )

    # ======================================================
    # GRÁFICO DE PREÇO
    # ======================================================

    st.divider()

    st.subheader(
        "📊 Evolução do Preço"
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
    # ANÁLISE DETALHADA
    # ======================================================

    st.divider()

    st.subheader(
        "🔎 Fundamentação da Análise"
    )

    analysis_col1, analysis_col2 = st.columns(
        2
    )

    # ------------------------------------------------------
    # JUSTIFICATIVAS
    # ------------------------------------------------------

    with analysis_col1:

        st.markdown(
            "### 📌 Justificativas"
        )

        if isinstance(
            reasons,
            list,
        ) and reasons:

            for reason in reasons:

                st.write(
                    f"✔ {reason}"
                )

        else:

            st.info(
                "Nenhuma justificativa foi retornada."
            )

    # ------------------------------------------------------
    # RISCO
    # ------------------------------------------------------

    with analysis_col2:

        st.markdown(
            "### 🛡️ Gestão de Risco"
        )

        st.write(
            f"{risk_icon(risk)} **{risk}**"
        )

        st.write(
            f"**Score Integrado:** "
            f"{integrated_score}/100"
        )

        st.write(
            f"**Tendência:** "
            f"{trend}"
        )

        st.write(
            f"**RSI:** "
            f"{rsi_status}"
        )

        st.write(
            f"**Sinal:** "
            f"{qualified_signal}"
        )

        st.write(
            f"**Recomendação:** "
            f"{recommendation}"
        )

    # ======================================================
    # RESUMO FINAL
    # ======================================================

    st.divider()

    st.subheader(
        "📋 Resumo Final da Análise"
    )

    summary1, summary2, summary3 = st.columns(
        3
    )

    with summary1:

        st.markdown(
            "### 📈 Técnico"
        )

        st.write(
            f"**Score:** "
            f"{technical_score}/100"
            if technical_score is not None
            else "**Score:** N/D"
        )

        st.write(
            f"**Classificação:** "
            f"{technical_classification}"
        )

        st.write(
            f"**Tendência:** "
            f"{trend}"
        )

    with summary2:

        st.markdown(
            "### 🏢 Fundamentalista"
        )

        st.write(
            f"**Score:** "
            f"{fundamental_score}/100"
            if fundamental_score is not None
            else "**Score:** N/D"
        )

        st.write(
            f"**Status:** "
            f"{fundamental_status}"
        )

        st.write(
            f"**Cobertura:** "
            f"{safe_number(fundamental_completeness, 0) * 100:.0f}%"
        )

    with summary3:

        st.markdown(
            "### ⭐ Integrado"
        )

        st.write(
            f"**Score:** "
            f"{integrated_score}/100"
        )

        st.write(
            f"**Classificação:** "
            f"{integrated_classification}"
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
### Como funciona o InvestIA PRO

**1. Análise Técnica**
- Preço atual
- Média móvel de 21 períodos
- Média móvel de 200 períodos
- RSI
- Volatilidade

**2. Análise Fundamentalista**
- P/L
- P/VP
- Dividend Yield
- ROE
- Margem de Lucro
- Dívida/Patrimônio

**3. Score Integrado**
- Combina análise técnica e fundamentalista
- Peso técnico padrão: 55%
- Peso fundamentalista padrão: 45%
- Quando os fundamentos não estão disponíveis, utiliza o Score Técnico

**Exemplos de ativos brasileiros:**
PETR4, VALE3, ITUB4, BBAS3, WEGE3, BBDC4.
"""
    )
