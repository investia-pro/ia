"""
InvestIA PRO
Aplicação Principal

Versão: v0.7
Fase: 3.0.6

Dashboard Integrado:
- Score Técnico
- Score Fundamentalista
- Score Integrado

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
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .investia-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
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
        margin-bottom: 0.8rem;
    }

    .score-card {
        padding: 1.2rem;
        border-radius: 12px;
        background-color: white;
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
        color: #0f172a;
    }

    .score-description {
        color: #475569;
        font-size: 0.9rem;
        margin-top: 0.3rem;
    }

    .executive-card {
        background-color: white;
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

    # Ativo já possui mercado
    if "." in asset:
        return asset

    # Ações brasileiras
    if (
        len(asset) in (5, 6)
        and asset[-1].isdigit()
    ):
        return f"{asset}.SA"

    return asset


def get_dict_value(
    data,
    key,
    default=None,
):
    """
    Obtém valor de dicionário com segurança.
    """

    if not isinstance(data, dict):
        return default

    return data.get(
        key,
        default,
    )


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
                Classificação: {classification}
            </div>

            <div class="score-description">
                Sinal: {signal}
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

        if not isinstance(
            item,
            dict,
        ):
            continue

        if key in (
            "base",
            "score",
            "raw_score",
            "final_score",
        ):
            continue

        rows.append(
            {
                "Indicador": key.upper(),
                "Pontos": item.get(
                    "points",
                    0,
                ),
                "Sinal": item.get(
                    "signal",
                    "N/D",
                ),
                "Análise": item.get(
                    "reason",
                    "N/D",
                ),
            }
        )

    if not rows:

        st.info(
            "Não há dados disponíveis para detalhar o Score."
        )

        return

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
    )


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.title("📈 InvestIA PRO")

    st.caption(
        "Fase 3.0.6"
    )

    st.divider()

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
        "Score Integrado"
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
            "Ex.: PETR4, VALE3, ITUB4 ou AAPL"
        ),
    )

with button_col:

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
        "**Analisar**."
    )

    st.markdown(
        """
        ### Recursos disponíveis

        - 📊 Score Técnico
        - 🏢 Score Fundamentalista
        - 🚀 Score Integrado
        - 📈 Indicadores técnicos
        - 🧭 Tendência e recomendação
        - ⚠️ Gestão de risco
        - 🔬 Explicabilidade dos Scores
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

st.subheader(
    f"📊 Analisando: {asset}"
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

except Exception as error:

    st.error(
        "❌ Erro ao carregar os módulos do InvestIA PRO."
    )

    st.code(
        traceback.format_exc()
    )

    st.warning(
        "O erro está em um dos arquivos: "
        "market.py, indicators.py ou analysis.py."
    )

    st.stop()


# ==========================================================
# BUSCA DE DADOS
# ==========================================================

try:

    with st.spinner(
        f"Buscando dados de {asset}..."
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
# INDICADORES
# ==========================================================

try:

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
# PREÇO
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
        "Dados preparados:"
    )

    st.write(
        list(prepared_data.keys())
    )

    st.write(
        "Indicadores:"
    )

    st.write(
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
# DADOS DA ANÁLISE
# ==========================================================

analysis_data = {

    "asset": asset,

    "price": current_price,

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

    "fundamentals": fundamentals,
}


# ==========================================================
# ANÁLISE
# ==========================================================

try:

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
# EXTRAÇÃO DOS RESULTADOS
# ==========================================================

technical_score = analysis.get(
    "technical_score",
    0,
)

technical_classification = analysis.get(
    "technical_classification",
    "N/D",
)

technical_signal = analysis.get(
    "technical_signal",
    "N/D",
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
    "N/D",
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
    "Resumo não disponível.",
)

qualified_signal = analysis.get(
    "qualified_signal",
    "N/D",
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
# PREÇO E INDICADORES
# ==========================================================

st.divider()

st.subheader(
    "📌 Indicadores Principais"
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
        format_currency(ma21)
        if ma21 is not None
        else "N/D",
    )

with metric_col3:

    ma200 = indicators.get(
        "ma200"
    )

    st.metric(
        "MA200",
        format_currency(ma200)
        if ma200 is not None
        else "N/D",
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
# FATORES
# ==========================================================

st.markdown(
    """
    <div class="section-title">
        🔎 Principais Fatores
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
        "Nenhum fator adicional disponível."
    )


# ==========================================================
# FUNDAMENTOS
# ==========================================================

st.markdown(
    """
    <div class="section-title">
        🏢 Dados Fundamentalistas
    </div>
    """,
    unsafe_allow_html=True,
)

fundamental_rows = []

for key, value in fundamentals.items():

    if value is None:
        continue

    fundamental_rows.append(
        {
            "Indicador": key,
            "Valor": value,
        }
    )

if fundamental_rows:

    st.dataframe(
        pd.DataFrame(
            fundamental_rows
        ),
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "Dados fundamentalistas não disponíveis para este ativo."
    )


# ==========================================================
# EXPLICABILIDADE
# ==========================================================

st.markdown(
    """
    <div class="section-title">
        🔬 Explicabilidade dos Scores
    </div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2 = st.tabs(
    [
        "📊 Score Técnico",
        "🏢 Score Fundamentalista",
    ]
)

with tab1:

    display_breakdown(
        technical_breakdown
    )

with tab2:

    display_breakdown(
        fundamental_breakdown
    )


# ==========================================================
# DEBUG
# ==========================================================

with st.expander(
    "🔧 Diagnóstico técnico"
):

    st.write(
        "Ativo:",
        asset,
    )

    st.write(
        "Dados preparados:",
        list(prepared_data.keys()),
    )

    st.write(
        "Indicadores:",
        list(indicators.keys()),
    )

    st.write(
        "Resultado da análise:",
        list(analysis.keys()),
    )


# ==========================================================
# RODAPÉ
# ==========================================================

st.divider()

st.caption(
    "InvestIA PRO • Fase 3.0.6 • "
    "Análise educacional e informativa. "
    "Não constitui recomendação individual de investimento."
)
