"""
InvestIA PRO
Aplicação Principal

Versão: v0.7.3
Fase: 3.0.7

Dashboard Integrado:
- Score Técnico
- Score Fundamentalista
- Score Integrado
- Gráficos de mercado
- Gráficos técnicos
- Gráficos fundamentalistas
- Comparação dos Scores
- Diagnóstico técnico seguro

Compatível com:
- market.py Fase 3.0.7
- indicators.py Fase 3.0.7
- score.py Fase 3.0.7
- analysis.py Fase 3.0.7
- charts.py Fase 3.0.7

IMPORTANTE:
Os módulos do projeto são importados somente
quando o usuário solicita uma análise.

Isso evita que uma falha em outro módulo
deixe a aplicação inteira em tela branca.
"""

import streamlit as st
import pandas as pd
import traceback


# ==========================================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================================

st.set_page_config(
    page_title="InvestIA PRO",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# CSS
# ==========================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1600px;
    }

    .investia-title {
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        color: #0f172a;
    }

    .investia-subtitle {
        font-size: 1rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }

    .section-title {
        font-size: 1.3rem;
        font-weight: 750;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
        color: #0f172a;
    }

    .score-card {
        padding: 1.2rem;
        border-radius: 14px;
        background-color: white;
        border: 1px solid #e2e8f0;
        min-height: 160px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
    }

    .score-label {
        color: #64748b;
        font-size: 0.95rem;
        font-weight: 700;
    }

    .score-value {
        font-size: 2.4rem;
        font-weight: 800;
        margin-top: 0.3rem;
        color: #0f172a;
    }

    .score-description {
        color: #475569;
        font-size: 0.9rem;
        margin-top: 0.35rem;
    }

    .executive-card {
        background-color: white;
        padding: 1.2rem;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        color: #334155;
        line-height: 1.6;
    }

    .analysis-status {
        padding: 0.9rem 1rem;
        border-radius: 10px;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        color: #475569;
        margin-bottom: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def safe_float(value, default=None):
    """
    Converte um valor para float com segurança.
    """

    if value is None:
        return default

    try:
        value = float(value)

    except (
        TypeError,
        ValueError,
    ):
        return default

    if pd.isna(value):
        return default

    return value


def format_currency(value):
    """
    Formata valor em Real brasileiro.
    """

    value = safe_float(
        value,
        0,
    )

    formatted = f"{value:,.2f}"

    formatted = (
        formatted
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"R$ {formatted}"


def format_number(
    value,
    decimals=2,
):
    """
    Formata número no padrão brasileiro.
    """

    value = safe_float(value)

    if value is None:
        return "N/D"

    formatted = f"{value:,.{decimals}f}"

    return (
        formatted
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def format_percent(value):
    """
    Formata percentual.
    """

    value = safe_float(value)

    if value is None:
        return "N/D"

    if abs(value) <= 1:
        value = value * 100

    return (
        f"{value:.2f}%"
        .replace(".", ",")
    )


def normalize_asset_input(asset):
    """
    Normaliza o código do ativo.

    Exemplos:

    PETR4 -> PETR4.SA
    VALE3 -> VALE3.SA
    AAPL  -> AAPL
    BTC-USD -> BTC-USD
    ^BVSP -> ^BVSP
    """

    if asset is None:
        return None

    asset = str(asset).strip().upper()

    if not asset:
        return None

    # Índices
    if asset.startswith("^"):
        return asset

    # Criptomoedas
    if "-" in asset:
        return asset

    # Ativo já possui sufixo de mercado
    if "." in asset:
        return asset

    # Ações brasileiras
    if (
        len(asset) in (5, 6)
        and asset[-1].isdigit()
    ):
        return f"{asset}.SA"

    return asset


def find_price(
    prepared_data,
    indicators,
):
    """
    Procura o preço atual em diferentes
    estruturas utilizadas pelo projeto.
    """

    possible_keys = [
        "price",
        "current_price",
        "close",
        "last_price",
    ]

    # ------------------------------------------------------
    # INDICADORES
    # ------------------------------------------------------

    if isinstance(indicators, dict):

        for key in possible_keys:

            value = safe_float(
                indicators.get(key)
            )

            if value is not None:
                return value

    # ------------------------------------------------------
    # DADOS PREPARADOS
    # ------------------------------------------------------

    if isinstance(prepared_data, dict):

        for key in possible_keys:

            value = safe_float(
                prepared_data.get(key)
            )

            if value is not None:
                return value

    # ------------------------------------------------------
    # HISTÓRICO
    # ------------------------------------------------------

    if isinstance(prepared_data, dict):

        history = prepared_data.get(
            "history"
        )

        if (
            history is not None
            and hasattr(history, "empty")
            and not history.empty
        ):

            possible_columns = [
                "Close",
                "Adj Close",
                "close",
                "adj_close",
            ]

            for column in possible_columns:

                if column in history.columns:

                    value = safe_float(
                        history[column].iloc[-1]
                    )

                    if value is not None:
                        return value

    return None


def display_score_card(
    label,
    score,
    classification,
    signal,
):
    """
    Exibe um card de Score.
    """

    score = safe_float(
        score,
        0,
    )

    # Garante Score entre 0 e 100
    score = max(
        0,
        min(
            100,
            score,
        ),
    )

    classification = (
        classification
        or "N/D"
    )

    signal = (
        signal
        or "N/D"
    )

    st.markdown(
        f"""
        <div class="score-card">

            <div class="score-label">
                {label}
            </div>

            <div class="score-value">
                {score:.0f}/100
            </div>

            <div class="score-description">
                Classificação: <b>{classification}</b>
            </div>

            <div class="score-description">
                Sinal: <b>{signal}</b>
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


def display_breakdown(
    breakdown,
):
    """
    Exibe detalhamento de um Score.
    """

    if not isinstance(
        breakdown,
        dict,
    ):

        st.info(
            "Detalhamento não disponível."
        )

        return

    rows = []

    for key, item in breakdown.items():

        # Alguns breakdowns possuem valores simples
        if not isinstance(
            item,
            dict,
        ):
            continue

        # Campos-resumo não devem aparecer
        if key.lower() in (
            "base",
            "score",
            "raw_score",
            "final_score",
            "total",
        ):
            continue

        points = item.get(
            "points",
            item.get(
                "score",
                item.get(
                    "value",
                    0,
                ),
            ),
        )

        signal = item.get(
            "signal",
            item.get(
                "status",
                "N/D",
            ),
        )

        reason = item.get(
            "reason",
            item.get(
                "description",
                item.get(
                    "analysis",
                    "N/D",
                ),
            ),
        )

        rows.append(
            {
                "Indicador": str(
                    key
                ).replace(
                    "_",
                    " "
                ).upper(),

                "Pontos": points,

                "Sinal": signal,

                "Análise": reason,
            }
        )

    if not rows:

        st.info(
            "Não há dados disponíveis para detalhar este Score."
        )

        return

    dataframe = pd.DataFrame(
        rows
    )

    st.dataframe(
        dataframe,
        use_container_width=True,
        hide_index=True,
    )


def render_chart(
    figure,
    message="Gráfico não disponível.",
    height=None,
):
    """
    Renderiza um gráfico Plotly com segurança.
    """

    if figure is None:

        st.info(message)

        return

    try:

        st.plotly_chart(
            figure,
            use_container_width=True,
            theme="streamlit",
        )

    except Exception as error:

        st.warning(
            message
        )

        with st.expander(
            "Ver erro do gráfico"
        ):

            st.code(
                traceback.format_exc()
            )


def clean_fundamental_value(
    key,
    value,
):
    """
    Formata valores fundamentalistas para exibição.
    """

    numeric_value = safe_float(value)

    if numeric_value is None:
        return str(value)

    percentage_keys = [
        "yield",
        "margin",
        "growth",
        "return",
        "roe",
        "roa",
        "beta",
    ]

    key_lower = str(key).lower()

    if any(
        term in key_lower
        for term in percentage_keys
    ):

        if (
            "beta"
            not in key_lower
        ):

            return format_percent(
                numeric_value
            )

    currency_keys = [
        "marketcap",
        "market_cap",
        "enterprisevalue",
        "revenue",
        "income",
        "cash",
        "debt",
        "ebitda",
    ]

    if any(
        term in key_lower
        for term in currency_keys
    ):

        if abs(numeric_value) >= 1_000_000_000:
            return (
                f"R$ "
                f"{numeric_value / 1_000_000_000:.2f} Bi"
                .replace(".", ",")
            )

        if abs(numeric_value) >= 1_000_000:
            return (
                f"R$ "
                f"{numeric_value / 1_000_000:.2f} Mi"
                .replace(".", ",")
            )

    return format_number(
        numeric_value
    )


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.title(
        "📈 InvestIA PRO"
    )

    st.caption(
        "Fase 3.0.7"
    )

    st.divider()

    st.subheader(
        "⚙️ Configurações"
    )

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

    st.divider()

    st.subheader(
        "🎯 Score Integrado"
    )

    technical_weight_percent = st.slider(
        "Peso Técnico (%)",
        min_value=0,
        max_value=100,
        value=50,
        step=5,
    )

    fundamental_weight_percent = (
        100
        - technical_weight_percent
    )

    st.write(
        f"Peso Fundamentalista: "
        f"**{fundamental_weight_percent}%**"
    )

    technical_weight = (
        technical_weight_percent / 100
    )

    fundamental_weight = (
        fundamental_weight_percent / 100
    )

    st.divider()

    st.caption(
        "Os pesos definem a composição "
        "do Score Integrado."
    )


# ==========================================================
# CABEÇALHO
# ==========================================================

st.markdown(
    """
    <div class="investia-title">
        📈 InvestIA PRO
    </div>

    <div class="investia-subtitle">
        Inteligência para análise de investimentos
    </div>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# ENTRADA
# ==========================================================

input_col, button_col = st.columns(
    [4, 1]
)

with input_col:

    asset_input = st.text_input(
        "Código do ativo",
        value="PETR4",
        placeholder=(
            "Ex.: PETR4, VALE3, ITUB4, AAPL ou BTC-USD"
        ),
    )

with button_col:

    st.write("")
    st.write("")

    analyze_button = st.button(
        "🔎 Analisar",
        use_container_width=True,
        type="primary",
    )


# ==========================================================
# TELA INICIAL
# ==========================================================

if not analyze_button:

    st.divider()

    st.info(
        "Digite o código de um ativo e clique em "
        "**Analisar** para iniciar."
    )

    feature_col1, feature_col2, feature_col3 = (
        st.columns(3)
    )

    with feature_col1:

        st.markdown(
            """
            ### 📊 Análise Técnica

            - Preço
            - MA21
            - MA200
            - RSI
            - Volume
            - Tendência
            """
        )

    with feature_col2:

        st.markdown(
            """
            ### 🏢 Análise Fundamentalista

            - P/L
            - P/VP
            - ROE
            - Margens
            - Crescimento
            - Endividamento
            """
        )

    with feature_col3:

        st.markdown(
            """
            ### 🚀 Inteligência Integrada

            - Score Técnico
            - Score Fundamentalista
            - Score Integrado
            - Recomendação
            - Gestão de Risco
            - Explicabilidade
            """
        )

    st.stop()


# ==========================================================
# NORMALIZAÇÃO
# ==========================================================

asset = normalize_asset_input(
    asset_input
)

if not asset:

    st.error(
        "Informe um ativo válido."
    )

    st.stop()


# ==========================================================
# STATUS
# ==========================================================

st.divider()

st.markdown(
    f"""
    <div class="analysis-status">
        🔎 Ativo em análise: <b>{asset}</b>
        &nbsp; | &nbsp;
        Período: <b>{period}</b>
        &nbsp; | &nbsp;
        Técnico: <b>{technical_weight_percent}%</b>
        &nbsp; | &nbsp;
        Fundamentalista: <b>{fundamental_weight_percent}%</b>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# IMPORTAÇÃO SEGURA DOS MÓDULOS
# ==========================================================

try:

    from market import (
        get_market_data,
        prepare_market_data,
    )

    from indicators import (
        calculate_indicators,
    )

    from analysis import (
        analyze_asset,
    )

    from charts import (
        create_dashboard_charts,
    )


except Exception:

    st.error(
        "❌ Erro ao carregar os módulos do InvestIA PRO."
    )

    st.warning(
        "Verifique os arquivos: market.py, "
        "indicators.py, analysis.py e charts.py."
    )

    st.code(
        traceback.format_exc()
    )

    st.stop()


# ==========================================================
# BUSCA DE DADOS
# ==========================================================

try:

    with st.spinner(
        f"Buscando dados de mercado de {asset}..."
    ):

        market_data = get_market_data(
            asset,
            period=period,
        )

    if market_data is None:

        st.error(
            f"Não foi possível obter dados para {asset}."
        )

        st.stop()


except Exception:

    st.error(
        "❌ Erro ao buscar dados de mercado."
    )

    st.code(
        traceback.format_exc()
    )

    st.stop()


# ==========================================================
# PREPARAÇÃO DOS DADOS
# ==========================================================

try:

    with st.spinner(
        "Preparando dados..."
    ):

        prepared_data = prepare_market_data(
            market_data
        )

    if not isinstance(
        prepared_data,
        dict,
    ):

        st.error(
            "prepare_market_data() não retornou um dicionário."
        )

        st.write(
            "Tipo retornado:",
            type(prepared_data)
        )

        st.stop()


except Exception:

    st.error(
        "❌ Erro ao preparar os dados."
    )

    st.code(
        traceback.format_exc()
    )

    st.stop()


# ==========================================================
# VALIDAÇÃO DO HISTÓRICO
# ==========================================================

history = prepared_data.get(
    "history"
)

if history is None:

    st.error(
        "❌ Os dados preparados não possuem histórico de preços."
    )

    st.write(
        "Chaves disponíveis:",
        list(prepared_data.keys())
    )

    st.stop()


if hasattr(
    history,
    "empty"
) and history.empty:

    st.error(
        "❌ O histórico de preços está vazio."
    )

    st.stop()


# ==========================================================
# INDICADORES
# ==========================================================

try:

    with st.spinner(
        "Calculando indicadores técnicos..."
    ):

        indicators = calculate_indicators(
            prepared_data
        )

    if not isinstance(
        indicators,
        dict,
    ):

        st.error(
            "calculate_indicators() não retornou um dicionário."
        )

        st.write(
            "Tipo retornado:",
            type(indicators)
        )

        st.stop()


except Exception:

    st.error(
        "❌ Erro ao calcular os indicadores."
    )

    st.code(
        traceback.format_exc()
    )

    st.stop()


# ==========================================================
# PREÇO ATUAL
# ==========================================================

current_price = find_price(
    prepared_data,
    indicators,
)

if current_price is None:

    st.error(
        "❌ Não foi possível identificar o preço atual."
    )

    st.write(
        "Dados preparados:",
        list(prepared_data.keys())
    )

    st.write(
        "Indicadores:",
        list(indicators.keys())
    )

    st.stop()


# ==========================================================
# FUNDAMENTOS
# ==========================================================

fundamentals = prepared_data.get(
    "fundamentals",
    {}
)

if not isinstance(
    fundamentals,
    dict,
):
    fundamentals = {}


# ==========================================================
# DADOS PARA ANÁLISE
# ==========================================================

analysis_data = {

    "asset": asset,

    "price": current_price,

    "current_price": current_price,

    "ma21": indicators.get(
        "ma21"
    ),

    "ma200": indicators.get(
        "ma200"
    ),

    "rsi": indicators.get(
        "rsi"
    ),

    "volatility": indicators.get(
        "volatility"
    ),

    "relative_volume": indicators.get(
        "relative_volume"
    ),

    "distance_ma21": indicators.get(
        "distance_ma21"
    ),

    "distance_ma200": indicators.get(
        "distance_ma200"
    ),

    "range_position": indicators.get(
        "range_position"
    ),

    "fundamentals": fundamentals,
}


# ==========================================================
# ANÁLISE
# ==========================================================

try:

    with st.spinner(
        "Executando motor de análise InvestIA..."
    ):

        analysis = analyze_asset(
            analysis_data,
            asset=asset,
            technical_weight=technical_weight,
            fundamental_weight=fundamental_weight,
        )

    if not isinstance(
        analysis,
        dict,
    ):

        st.error(
            "analyze_asset() não retornou um dicionário."
        )

        st.write(
            "Tipo retornado:",
            type(analysis)
        )

        st.stop()


except Exception:

    st.error(
        "❌ Erro no motor de análise."
    )

    st.code(
        traceback.format_exc()
    )

    st.stop()


# ==========================================================
# GARANTE FUNDAMENTOS NO RESULTADO
# ==========================================================

if not isinstance(
    analysis.get(
        "fundamentals"
    ),
    dict,
):
    analysis["fundamentals"] = fundamentals


# ==========================================================
# EXTRAÇÃO DOS RESULTADOS
# ==========================================================

technical_score = analysis.get(
    "technical_score",
    0,
)

technical_classification = analysis.get(
    "technical_classification",
    analysis.get(
        "classification",
        "N/D",
    ),
)

technical_signal = analysis.get(
    "technical_signal",
    analysis.get(
        "signal",
        "N/D",
    ),
)


fundamental_score = analysis.get(
    "fundamental_score",
    0,
)

fundamental_classification = analysis.get(
    "fundamental_classification",
    "N/D",
)

fundamental_signal = analysis.get(
    "fundamental_signal",
    "N/D",
)


integrated_score = analysis.get(
    "integrated_score",
    analysis.get(
        "score",
        0,
    ),
)

integrated_classification = analysis.get(
    "integrated_classification",
    analysis.get(
        "classification",
        "N/D",
    ),
)

integrated_signal = analysis.get(
    "integrated_signal",
    analysis.get(
        "signal",
        "N/D",
    ),
)


trend = analysis.get(
    "trend",
    indicators.get(
        "trend",
        "N/D",
    ),
)

risk = analysis.get(
    "risk",
    "N/D",
)

recommendation = analysis.get(
    "recommendation",
    "AGUARDAR",
)

executive_summary = analysis.get(
    "executive_summary",
    "Resumo executivo não disponível.",
)

qualified_signal = analysis.get(
    "qualified_signal",
    integrated_signal,
)

signal_icon = analysis.get(
    "signal_icon",
    "⚪",
)

reasons = analysis.get(
    "reasons",
    [],
)

technical_breakdown = analysis.get(
    "technical_breakdown",
    analysis.get(
        "breakdown",
        {},
    ),
)

fundamental_breakdown = analysis.get(
    "fundamental_breakdown",
    {},
)


# ==========================================================
# GRÁFICOS
# ==========================================================

try:

    charts = create_dashboard_charts(
        prepared_data=prepared_data,
        indicators=indicators,
        analysis=analysis,
        asset=asset,
    )


except Exception:

    charts = {}

    st.warning(
        "⚠️ A análise foi concluída, mas ocorreu um "
        "erro ao gerar parte dos gráficos."
    )

    with st.expander(
        "Ver diagnóstico dos gráficos"
    ):

        st.code(
            traceback.format_exc()
        )


# ==========================================================
# INDICADORES PRINCIPAIS
# ==========================================================

st.divider()

st.markdown(
    """
    <div class="section-title">
        📌 Indicadores Principais
    </div>
    """,
    unsafe_allow_html=True,
)

metric_col1, metric_col2, metric_col3, metric_col4 = (
    st.columns(4)
)


with metric_col1:

    st.metric(
        "Preço Atual",
        format_currency(
            current_price
        ),
    )


with metric_col2:

    ma21 = indicators.get(
        "ma21"
    )

    st.metric(
        "MA21",
        (
            format_currency(ma21)
            if safe_float(ma21) is not None
            else "N/D"
        ),
    )


with metric_col3:

    ma200 = indicators.get(
        "ma200"
    )

    st.metric(
        "MA200",
        (
            format_currency(ma200)
            if safe_float(ma200) is not None
            else "N/D"
        ),
    )


with metric_col4:

    st.metric(
        "RSI",
        format_number(
            indicators.get(
                "rsi"
            )
        ),
    )


# ==========================================================
# SCORES
# ==========================================================

st.markdown(
    """
    <div class="section-title">
        🎯 Scores InvestIA
    </div>
    """,
    unsafe_allow_html=True,
)

score_col1, score_col2, score_col3 = (
    st.columns(3)
)


with score_col1:

    display_score_card(
        "📊 Score Técnico",
        technical_score,
        technical_classification,
        technical_signal,
    )


with score_col2:

    display_score_card(
        "🏢 Score Fundamentalista",
        fundamental_score,
        fundamental_classification,
        fundamental_signal,
    )


with score_col3:

    display_score_card(
        "🚀 Score Integrado",
        integrated_score,
        integrated_classification,
        integrated_signal,
    )


# ==========================================================
# DECISÃO EXECUTIVA
# ==========================================================

st.markdown(
    """
    <div class="section-title">
        🧭 Decisão Executiva
    </div>
    """,
    unsafe_allow_html=True,
)

decision_col1, decision_col2, decision_col3 = (
    st.columns(3)
)


with decision_col1:

    st.metric(
        "Recomendação",
        f"{signal_icon} {recommendation}",
    )


with decision_col2:

    st.metric(
        "Tendência",
        trend,
    )


with decision_col3:

    st.metric(
        "Risco",
        risk,
    )


st.caption(
    f"Qualificação do sinal: {qualified_signal}"
)


# ==========================================================
# RESUMO EXECUTIVO
# ==========================================================

st.markdown(
    """
    <div class="section-title">
        📝 Resumo Executivo
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="executive-card">
        {executive_summary}
    </div>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# DASHBOARD GRÁFICO
# ==========================================================

st.markdown(
    """
    <div class="section-title">
        📈 Dashboard de Mercado
    </div>
    """,
    unsafe_allow_html=True,
)

chart_tab1, chart_tab2, chart_tab3 = st.tabs(
    [
        "📈 Mercado",
        "🎯 Scores e Técnico",
        "🏢 Fundamentalista",
    ]
)


# ==========================================================
# ABA MERCADO
# ==========================================================

with chart_tab1:

    price_chart = charts.get(
        "price"
    )

    render_chart(
        price_chart,
        "Gráfico de preços não disponível.",
    )

    market_col1, market_col2 = st.columns(2)

    with market_col1:

        volume_chart = charts.get(
            "volume"
        )

        render_chart(
            volume_chart,
            "Gráfico de volume não disponível.",
        )

    with market_col2:

        rsi_chart = charts.get(
            "rsi"
        )

        render_chart(
            rsi_chart,
            "Gráfico de RSI não disponível.",
        )

    performance_chart = charts.get(
        "performance"
    )

    render_chart(
        performance_chart,
        "Gráfico de desempenho não disponível.",
    )


# ==========================================================
# ABA SCORES E TÉCNICO
# ==========================================================

with chart_tab2:

    technical_col1, technical_col2 = st.columns(2)

    with technical_col1:

        score_chart = charts.get(
            "scores"
        )

        render_chart(
            score_chart,
            "Comparação dos Scores não disponível.",
        )

    with technical_col2:

        technical_chart = charts.get(
            "technical"
        )

        render_chart(
            technical_chart,
            "Panorama técnico não disponível.",
        )


# ==========================================================
# ABA FUNDAMENTALISTA
# ==========================================================

with chart_tab3:

    fundamental_chart = charts.get(
        "fundamentals"
    )

    render_chart(
        fundamental_chart,
        "Gráfico fundamentalista não disponível.",
    )

    st.markdown(
        """
        <div class="section-title">
            📋 Dados Fundamentalistas
        </div>
        """,
        unsafe_allow_html=True,
    )

    fundamental_rows = []

    if isinstance(
        fundamentals,
        dict,
    ):

        for key, value in fundamentals.items():

            if value is None:
                continue

            if isinstance(
                value,
                (
                    dict,
                    list,
                    tuple,
                ),
            ):
                continue

            fundamental_rows.append(
                {
                    "Indicador": str(
                        key
                    ),

                    "Valor": clean_fundamental_value(
                        key,
                        value,
                    ),
                }
            )

    if fundamental_rows:

        fundamental_dataframe = pd.DataFrame(
            fundamental_rows
        )

        st.dataframe(
            fundamental_dataframe,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "Dados fundamentalistas não disponíveis "
            "para este ativo."
        )


# ==========================================================
# PRINCIPAIS FATORES
# ==========================================================

st.markdown(
    """
    <div class="section-title">
        🔎 Principais Fatores da Análise
    </div>
    """,
    unsafe_allow_html=True,
)


if isinstance(
    reasons,
    list,
) and reasons:

    for reason in reasons:

        if reason is None:
            continue

        st.write(
            f"• {reason}"
        )


else:

    st.info(
        "Nenhum fator adicional foi retornado pelo "
        "motor de análise."
    )


# ==========================================================
# EXPLICABILIDADE DOS SCORES
# ==========================================================

st.markdown(
    """
    <div class="section-title">
        🔬 Explicabilidade dos Scores
    </div>
    """,
    unsafe_allow_html=True,
)

explain_tab1, explain_tab2 = st.tabs(
    [
        "📊 Score Técnico",
        "🏢 Score Fundamentalista",
    ]
)


with explain_tab1:

    display_breakdown(
        technical_breakdown
    )


with explain_tab2:

    display_breakdown(
        fundamental_breakdown
    )


# ==========================================================
# DETALHES ADICIONAIS
# ==========================================================

with st.expander(
    "📊 Ver dados técnicos completos"
):

    technical_rows = []

    for key, value in indicators.items():

        if isinstance(
            value,
            (
                dict,
                list,
                tuple,
                pd.DataFrame,
                pd.Series,
            ),
        ):
            continue

        technical_rows.append(
            {
                "Indicador": str(key),
                "Valor": value,
            }
        )

    if technical_rows:

        st.dataframe(
            pd.DataFrame(
                technical_rows
            ),
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "Não há indicadores adicionais disponíveis."
        )


# ==========================================================
# DIAGNÓSTICO TÉCNICO
# ==========================================================

with st.expander(
    "🔧 Diagnóstico técnico"
):

    st.write(
        "### Informações da execução"
    )

    st.write(
        "Ativo:",
        asset,
    )

    st.write(
        "Período:",
        period,
    )

    st.write(
        "Peso técnico:",
        f"{technical_weight_percent}%"
    )

    st.write(
        "Peso fundamentalista:",
        f"{fundamental_weight_percent}%"
    )

    st.divider()

    st.write(
        "### Estruturas carregadas"
    )

    st.write(
        "Dados preparados:",
        list(prepared_data.keys())
    )

    st.write(
        "Indicadores:",
        list(indicators.keys())
    )

    st.write(
        "Resultado da análise:",
        list(analysis.keys())
    )

    st.write(
        "Gráficos disponíveis:",
        list(charts.keys())
    )

    st.divider()

    st.write(
        "### Status dos dados"
    )

    st.write(
        "Preço identificado:",
        current_price is not None,
    )

    st.write(
        "Histórico disponível:",
        (
            history is not None
            and not history.empty
        ),
    )

    st.write(
        "Fundamentos disponíveis:",
        len(fundamentals),
    )

    st.write(
        "Score Técnico:",
        technical_score,
    )

    st.write(
        "Score Fundamentalista:",
        fundamental_score,
    )

    st.write(
        "Score Integrado:",
        integrated_score,
    )


# ==========================================================
# RODAPÉ
# ==========================================================

st.divider()

st.caption(
    "InvestIA PRO • Fase 3.0.7 • "
    "Análise educacional e informativa. "
    "Não constitui recomendação individual de investimento."
)
