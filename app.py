"""
InvestIA PRO
Aplicação Principal

Versão: v0.7
Fase: 3.0.6 - Dashboard Integrado Técnico + Fundamentalista

Responsabilidades:
- Interface principal Streamlit
- Busca de ativos
- Preparação dos dados
- Cálculo dos indicadores
- Análise técnica
- Análise fundamentalista
- Score integrado
- Dashboard executivo
"""

import streamlit as st
import pandas as pd

from market import get_market_data, prepare_market_data
from indicators import (
    calculate_indicators,
    get_current_price,
)
from analysis import analyze_asset


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

    .main {
        background-color: #f8fafc;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .investia-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0;
    }

    .investia-subtitle {
        font-size: 1rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 1.5rem;
        margin-bottom: 0.7rem;
    }

    .score-card {
        padding: 1.2rem;
        border-radius: 12px;
        background: white;
        border: 1px solid #e2e8f0;
        min-height: 150px;
    }

    .score-label {
        color: #64748b;
        font-size: 0.9rem;
        font-weight: 600;
    }

    .score-value {
        font-size: 2.2rem;
        font-weight: 800;
        margin-top: 0.3rem;
    }

    .score-description {
        color: #475569;
        font-size: 0.9rem;
        margin-top: 0.3rem;
    }

    .executive-card {
        background: white;
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
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
    Converte valores para float com segurança.
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
    Formata valores em Real brasileiro.
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
    Formata números no padrão brasileiro.
    """

    value = safe_float(
        value
    )

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
    Formata percentuais.

    Aceita:
    0.15 -> 15,00%
    15   -> 15,00%
    """

    value = safe_float(
        value
    )

    if value is None:
        return "N/D"

    if abs(value) <= 1:
        value = value * 100

    return (
        f"{value:.2f}%"
        .replace(".", ",")
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
    analysis,
    key,
    default=None,
):
    """
    Obtém um valor da análise com segurança.
    """

    if not isinstance(
        analysis,
        dict,
    ):
        return default

    return analysis.get(
        key,
        default,
    )


def normalize_asset_input(asset):
    """
    Normaliza o código do ativo.

    Exemplos:

    petr4     -> PETR4.SA
    PETR4     -> PETR4.SA
    PETR4.SA  -> PETR4.SA
    AAPL      -> AAPL
    """

    if not asset:
        return None

    asset = (
        str(asset)
        .strip()
        .upper()
    )

    if not asset:
        return None

    # Índices conhecidos
    if asset.startswith("^"):
        return asset

    # Criptomoedas
    if "-" in asset:
        return asset

    # Já possui sufixo
    if "." in asset:
        return asset

    # Ações brasileiras mais comuns
    if (
        len(asset) in (5, 6)
        and asset[-1].isdigit()
    ):
        return f"{asset}.SA"

    return asset


def display_score_card(
    label,
    score,
    classification,
    signal,
    description,
):
    """
    Renderiza um card de Score.
    """

    score = safe_float(
        score,
        0,
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
                {classification}
            </div>

            <div class="score-description">
                Sinal: {signal}
            </div>

            <div class="score-description">
                {description}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_breakdown(
    title,
    breakdown,
    indicators,
):
    """
    Exibe o detalhamento dos Scores.
    """

    st.subheader(title)

    if not isinstance(
        breakdown,
        dict,
    ):
        st.info(
            "Detalhamento não disponível."
        )
        return

    rows = []

    for key, label in indicators:

        item = breakdown.get(
            key,
            {}
        )

        if not isinstance(
            item,
            dict,
        ):
            continue

        points = item.get(
            "points",
            0,
        )

        signal = item.get(
            "signal",
            "N/D",
        )

        reason = item.get(
            "reason",
            "N/D",
        )

        rows.append(
            {
                "Indicador": label,
                "Pontos": points,
                "Sinal": signal,
                "Análise": reason,
            }
        )

    if not rows:

        st.info(
            "Não há dados suficientes para "
            "exibir o detalhamento."
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


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.title("⚙️ InvestIA PRO")

    st.markdown(
        "---"
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

    st.markdown(
        "---"
    )

    st.markdown(
        "### Pesos do Score Integrado"
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

    st.caption(
        f"Peso Fundamentalista: "
        f"{fundamental_weight_percent}%"
    )

    technical_weight = (
        technical_weight_percent
        / 100
    )

    fundamental_weight = (
        fundamental_weight_percent
        / 100
    )

    st.markdown(
        "---"
    )

    st.caption(
        "InvestIA PRO • Fase 3.0.6"
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
        Análise Técnica + Fundamentalista + Score Integrado
    </div>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# ENTRADA DO ATIVO
# ==========================================================

input_col, button_col = st.columns(
    [4, 1]
)

with input_col:

    asset_input = st.text_input(
        "Digite o código do ativo",
        value="PETR4",
        placeholder="Ex.: PETR4, VALE3, ITUB4, AAPL",
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
# INSTRUÇÃO INICIAL
# ==========================================================

if not analyze_button:

    st.info(
        "Digite um ativo e clique em "
        "**Analisar** para iniciar."
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
        "Informe um código de ativo válido."
    )

    st.stop()


# ==========================================================
# PROCESSAMENTO
# ==========================================================

try:

    with st.spinner(
        f"Buscando dados de {asset}..."
    ):

        # ==================================================
        # MERCADO
        # ==================================================

        market_data = get_market_data(
            asset,
            period=period,
        )

        if market_data is None:

            st.error(
                f"Não foi possível obter "
                f"dados para {asset}."
            )

            st.stop()

        # ==================================================
        # PREPARAÇÃO
        # ==================================================

        prepared_data = prepare_market_data(
            market_data
        )

        if not isinstance(
            prepared_data,
            dict,
        ):

            st.error(
                "Erro ao preparar os dados do ativo."
            )

            st.stop()

        history = prepared_data.get(
            "history"
        )

        if history is None:

            st.error(
                "O histórico de preços não foi encontrado."
            )

            st.stop()

        if hasattr(
            history,
            "empty",
        ) and history.empty:

            st.error(
                "O histórico de preços está vazio."
            )

            st.stop()

        # ==================================================
        # PREÇO
        # ==================================================

        current_price = get_current_price(
            prepared_data
        )

        if current_price is None:

            st.error(
                "Não foi possível identificar "
                "o preço atual do ativo."
            )

            st.stop()

        # ==================================================
        # INDICADORES
        # ==================================================

        indicators = calculate_indicators(
            prepared_data
        )

        if not isinstance(
            indicators,
            dict,
        ):

            st.error(
                "Não foi possível calcular "
                "os indicadores."
            )

            st.stop()

        # ==================================================
        # FUNDAMENTOS
        # ==================================================

        fundamentals = prepared_data.get(
            "fundamentals",
            {}
        )

        if not isinstance(
            fundamentals,
            dict,
        ):

            fundamentals = {}

        # ==================================================
        # DADOS PARA ANÁLISE
        # ==================================================

        analysis_data = {

            "asset": asset,

            "price": current_price,

            "ma21": get_indicator_value(
                indicators,
                "ma21",
            ),

            "ma200": get_indicator_value(
                indicators,
                "ma200",
            ),

            "rsi": get_indicator_value(
                indicators,
                "rsi",
            ),

            "volatility": get_indicator_value(
                indicators,
                "volatility",
            ),

            "fundamentals": fundamentals,
        }

        # ==================================================
        # ANÁLISE
        # ==================================================

        analysis = analyze_asset(

            analysis_data,

            asset=asset,

            technical_weight=
                technical_weight,

            fundamental_weight=
                fundamental_weight,
        )


except Exception as error:

    st.error(
        "Ocorreu um erro durante a análise."
    )

    st.exception(
        error
    )

    st.stop()


# ==========================================================
# EXTRAÇÃO DOS RESULTADOS
# ==========================================================

technical_score = get_analysis_value(
    analysis,
    "technical_score",
    0,
)

technical_classification = (
    get_analysis_value(
        analysis,
        "technical_classification",
        "N/D",
    )
)

technical_signal = get_analysis_value(
    analysis,
    "technical_signal",
    "N/D",
)


fundamental_score = get_analysis_value(
    analysis,
    "fundamental_score",
    0,
)

fundamental_classification = (
    get_analysis_value(
        analysis,
        "fundamental_classification",
        "N/D",
    )
)

fundamental_signal = get_analysis_value(
    analysis,
    "fundamental_signal",
    "N/D",
)


integrated_score = get_analysis_value(
    analysis,
    "integrated_score",
    get_analysis_value(
        analysis,
        "score",
        0,
    ),
)

integrated_classification = (
    get_analysis_value(
        analysis,
        "integrated_classification",
        get_analysis_value(
            analysis,
            "classification",
            "N/D",
        ),
    )
)

integrated_signal = get_analysis_value(
    analysis,
    "integrated_signal",
    get_analysis_value(
        analysis,
        "signal",
        "N/D",
    ),
)


fundamental_coverage = (
    get_analysis_value(
        analysis,
        "fundamental_coverage",
        0,
    )
)

fundamental_available_indicators = (
    get_analysis_value(
        analysis,
        "fundamental_available_indicators",
        0,
    )
)

fundamental_total_indicators = (
    get_analysis_value(
        analysis,
        "fundamental_total_indicators",
        0,
    )
)


trend = get_analysis_value(
    analysis,
    "trend",
    "N/D",
)

trend_level = get_analysis_value(
    analysis,
    "trend_level",
    "N/D",
)

rsi_status = get_analysis_value(
    analysis,
    "rsi_status",
    "N/D",
)

risk = get_analysis_value(
    analysis,
    "risk",
    "N/D",
)

recommendation = get_analysis_value(
    analysis,
    "recommendation",
    "AGUARDAR",
)

qualified_signal = get_analysis_value(
    analysis,
    "qualified_signal",
    "N/D",
)

signal_icon = get_analysis_value(
    analysis,
    "signal_icon",
    "⚪",
)

reasons = get_analysis_value(
    analysis,
    "reasons",
    [],
)

executive_summary = get_analysis_value(
    analysis,
    "executive_summary",
    "",
)

technical_breakdown = get_analysis_value(
    analysis,
    "technical_breakdown",
    {},
)

fundamental_breakdown = get_analysis_value(
    analysis,
    "fundamental_breakdown",
    {},
)


# ==========================================================
# TÍTULO DO ATIVO
# ==========================================================

st.markdown(
    "---"
)

st.subheader(
    f"📊 Análise de {asset}"
)


# ==========================================================
# MÉTRICAS DE MERCADO
# ==========================================================

price_col, ma21_col, ma200_col, rsi_col = (
    st.columns(4)
)

with price_col:

    st.metric(
        "Preço Atual",
        format_currency(
            current_price
        ),
    )

with ma21_col:

    st.metric(
        "MA21",
        format_currency(
            get_indicator_value(
                indicators,
                "ma21",
            )
        )
        if get_indicator_value(
            indicators,
            "ma21",
        ) is not None
        else "N/D",
    )

with ma200_col:

    st.metric(
        "MA200",
        format_currency(
            get_indicator_value(
                indicators,
                "ma200",
            )
        )
        if get_indicator_value(
            indicators,
            "ma200",
        ) is not None
        else "N/D",
    )

with rsi_col:

    rsi_value = get_indicator_value(
        indicators,
        "rsi",
    )

    st.metric(
        "RSI",
        format_number(
            rsi_value
        )
        if rsi_value is not None
        else "N/D",
    )


# ==========================================================
# SCORE PRINCIPAL
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

        label="📊 Score Técnico",

        score=technical_score,

        classification=
            technical_classification,

        signal=
            technical_signal,

        description=(
            "Avaliação baseada em preço, "
            "MA21, MA200 e RSI."
        ),
    )

with score_col2:

    display_score_card(

        label="🏢 Score Fundamentalista",

        score=fundamental_score,

        classification=
            fundamental_classification,

        signal=
            fundamental_signal,

        description=(
            f"Cobertura: "
            f"{safe_float(fundamental_coverage, 0):.0f}% "
            f"dos indicadores."
        ),
    )

with score_col3:

    display_score_card(

        label="🚀 Score Integrado",

        score=integrated_score,

        classification=
            integrated_classification,

        signal=
            integrated_signal,

        description=(
            f"{technical_weight_percent}% Técnico + "
            f"{fundamental_weight_percent}% Fundamentalista."
        ),
    )


# ==========================================================
# RECOMENDAÇÃO EXECUTIVA
# ==========================================================

st.markdown(
    """
    <div class="section-title">
        🧭 Decisão Executiva
    </div>
    """,
    unsafe_allow_html=True,
)

decision_col1, decision_col2, decision_col3, decision_col4 = (
    st.columns(4)
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
        trend_level,
    )

with decision_col3:

    st.metric(
        "Risco",
        risk,
    )

with decision_col4:

    st.metric(
        "RSI",
        rsi_status,
    )

st.caption(
    f"Qualificação do sinal: "
    f"{qualified_signal}"
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

        st.write(
            f"• {reason}"
        )

else:

    st.info(
        "Não há fatores adicionais disponíveis."
    )


# ==========================================================
# GRÁFICO DE PREÇOS
# ==========================================================

st.markdown(
    """
    <div class="section-title">
        📈 Histórico de Preços
    </div>
    """,
    unsafe_allow_html=True,
)

try:

    import plotly.graph_objects as go

    if (
        history is not None
        and not history.empty
    ):

        price_column = None

        possible_columns = [
            "Close",
            "Adj Close",
            "close",
            "adj_close",
        ]

        for column in possible_columns:

            if column in history.columns:

                price_column = column
                break

        if price_column is not None:

            figure = go.Figure()

            figure.add_trace(

                go.Scatter(

                    x=history.index,

                    y=history[
                        price_column
                    ],

                    mode="lines",

                    name="Preço",
                )
            )

            figure.update_layout(

                title=f"Histórico de {asset}",

                xaxis_title="Data",

                yaxis_title="Preço",

                height=420,

                margin=dict(
                    l=20,
                    r=20,
                    t=50,
                    b=20,
                ),
            )

            st.plotly_chart(
                figure,
                use_container_width=True,
            )

        else:

            st.info(
                "Não foi encontrada uma coluna "
                "de preços para o gráfico."
            )

except Exception as chart_error:

    st.warning(
        "Não foi possível carregar o gráfico."
    )

    st.caption(
        str(chart_error)
    )


# ==========================================================
# DADOS FUNDAMENTALISTAS
# ==========================================================

st.markdown(
    """
    <div class="section-title">
        🏢 Dados Fundamentalistas
    </div>
    """,
    unsafe_allow_html=True,
)

coverage_col1, coverage_col2, coverage_col3 = (
    st.columns(3)
)

with coverage_col1:

    st.metric(
        "Cobertura",
        f"{safe_float(fundamental_coverage, 0):.0f}%",
    )

with coverage_col2:

    st.metric(
        "Indicadores disponíveis",
        fundamental_available_indicators,
    )

with coverage_col3:

    st.metric(
        "Total avaliado",
        fundamental_total_indicators,
    )


fundamental_rows = [

    {
        "Indicador": "P/L",
        "Valor": fundamentals.get(
            "price_to_earnings",
            fundamentals.get(
                "trailing_pe",
                None,
            ),
        ),
    },

    {
        "Indicador": "P/VP",
        "Valor": fundamentals.get(
            "price_to_book",
            None,
        ),
    },

    {
        "Indicador": "ROE",
        "Valor": fundamentals.get(
            "return_on_equity",
            fundamentals.get(
                "roe",
                None,
            ),
        ),
    },

    {
        "Indicador": "Dividend Yield",
        "Valor": fundamentals.get(
            "dividend_yield",
            None,
        ),
    },

    {
        "Indicador": "Margem de Lucro",
        "Valor": fundamentals.get(
            "profit_margin",
            fundamentals.get(
                "profit_margins",
                None,
            ),
        ),
    },

    {
        "Indicador": "Crescimento da Receita",
        "Valor": fundamentals.get(
            "revenue_growth",
            None,
        ),
    },

    {
        "Indicador": "Dívida/Patrimônio",
        "Valor": fundamentals.get(
            "debt_to_equity",
            None,
        ),
    },
]


formatted_fundamental_rows = []

for row in fundamental_rows:

    indicator_name = row[
        "Indicador"
    ]

    value = row[
        "Valor"
    ]

    if indicator_name in [

        "ROE",

        "Dividend Yield",

        "Margem de Lucro",

        "Crescimento da Receita",
    ]:

        formatted_value = format_percent(
            value
        )

    elif indicator_name == "Dívida/Patrimônio":

        if value is None:

            formatted_value = "N/D"

        else:

            formatted_value = (
                f"{format_number(value)}%"
            )

    else:

        formatted_value = format_number(
            value
        )

    formatted_fundamental_rows.append(

        {

            "Indicador":
                indicator_name,

            "Valor":
                formatted_value,
        }
    )


st.dataframe(

    pd.DataFrame(
        formatted_fundamental_rows
    ),

    use_container_width=True,

    hide_index=True,
)


# ==========================================================
# DETALHAMENTO DOS SCORES
# ==========================================================

st.markdown(
    """
    <div class="section-title">
        🔬 Explicabilidade dos Scores
    </div>
    """,
    unsafe_allow_html=True,
)

technical_tab, fundamental_tab = st.tabs(

    [

        "📊 Score Técnico",

        "🏢 Score Fundamentalista",
    ]
)


# ==========================================================
# TAB TÉCNICA
# ==========================================================

with technical_tab:

    display_breakdown(

        title="Contribuição dos Indicadores Técnicos",

        breakdown=technical_breakdown,

        indicators=[

            (
                "ma21",
                "MA21",
            ),

            (
                "ma200",
                "MA200",
            ),

            (
                "rsi",
                "RSI",
            ),
        ],
    )


# ==========================================================
# TAB FUNDAMENTALISTA
# ==========================================================

with fundamental_tab:

    display_breakdown(

        title="Contribuição dos Fundamentos",

        breakdown=fundamental_breakdown,

        indicators=[

            (
                "price_to_earnings",
                "P/L",
            ),

            (
                "price_to_book",
                "P/VP",
            ),

            (
                "return_on_equity",
                "ROE",
            ),

            (
                "dividend_yield",
                "Dividend Yield",
            ),

            (
                "profit_margin",
                "Margem de Lucro",
            ),

            (
                "revenue_growth",
                "Crescimento da Receita",
            ),

            (
                "debt_to_equity",
                "Dívida/Patrimônio",
            ),
        ],
    )


# ==========================================================
# DADOS TÉCNICOS
# ==========================================================

with st.expander(
    "🔧 Dados técnicos detalhados"
):

    technical_rows = [

        {
            "Indicador": "Preço Atual",
            "Valor": format_currency(
                current_price
            ),
        },

        {
            "Indicador": "MA21",
            "Valor": format_currency(
                get_indicator_value(
                    indicators,
                    "ma21",
                )
            )
            if get_indicator_value(
                indicators,
                "ma21",
            ) is not None
            else "N/D",
        },

        {
            "Indicador": "MA200",
            "Valor": format_currency(
                get_indicator_value(
                    indicators,
                    "ma200",
                )
            )
            if get_indicator_value(
                indicators,
                "ma200",
            ) is not None
            else "N/D",
        },

        {
            "Indicador": "RSI",
            "Valor": format_number(
                get_indicator_value(
                    indicators,
                    "rsi",
                )
            ),
        },

        {
            "Indicador": "Volatilidade",
            "Valor": format_percent(
                get_indicator_value(
                    indicators,
                    "volatility",
                )
            ),
        },
    ]

    st.dataframe(

        pd.DataFrame(
            technical_rows
        ),

        use_container_width=True,

        hide_index=True,
    )


# ==========================================================
# RODAPÉ
# ==========================================================

st.markdown(
    "---"
)

st.caption(
    "InvestIA PRO • Fase 3.0.6 • "
    "Análise educacional e informativa. "
    "Não constitui recomendação individual "
    "de investimento."
)
