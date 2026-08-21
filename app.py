"""
InvestIA PRO
Aplicação Principal

Versão: v0.7
Fase: 3.0.5 - Dashboard Histórico e Evolução dos Scores

Responsabilidades:
- Buscar dados do mercado
- Preparar dados históricos
- Calcular indicadores
- Executar análise InvestIA
- Exibir Score Técnico
- Exibir Score Fundamentalista
- Exibir Score Integrado
- Exibir evolução histórica
- Exibir gráficos de preço e Score
"""

import streamlit as st
import pandas as pd

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
    create_price_indicators_chart,
    create_score_evolution_chart,
    create_integrated_analysis_chart,
    create_scores_comparison_chart,
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
    "Dashboard inteligente para análise técnica, "
    "fundamentalista e evolução histórica de ativos."
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


def safe_dict(value):
    """
    Garante o retorno de um dicionário.
    """

    if isinstance(
        value,
        dict,
    ):
        return value

    return {}


def safe_float(
    value,
    default=None,
):
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


def safe_text(
    value,
    default="",
):
    """
    Converte valores para texto.
    """

    if value is None:
        return default

    value = str(value).strip()

    if not value:
        return default

    return value


def get_indicator_value(
    indicators,
    key,
    default=None,
):
    """
    Obtém um indicador com segurança.
    """

    indicators = safe_dict(
        indicators
    )

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
    Obtém um valor do resultado da análise,
    aceitando nomes alternativos.
    """

    result = safe_dict(
        result
    )

    for key in keys:

        if key in result:

            value = result.get(
                key
            )

            if value is not None:

                return value

    return default


def get_historical_indicators(
    indicators,
    prepared_data,
):
    """
    Procura o histórico de indicadores
    em diferentes estruturas possíveis.

    Mantém compatibilidade com versões
    anteriores do indicators.py.
    """

    indicators = safe_dict(
        indicators
    )

    possible_keys = [

        "historical",
        "history",
        "historical_indicators",
        "indicators_history",

    ]

    for key in possible_keys:

        value = indicators.get(
            key
        )

        if isinstance(
            value,
            pd.DataFrame,
        ):

            if not value.empty:

                return value

    # ------------------------------------------------------
    # FALLBACK
    # ------------------------------------------------------
    # Caso o indicators.py não retorne
    # o histórico diretamente.

    prepared_data = safe_dict(
        prepared_data
    )

    history = prepared_data.get(
        "history"
    )

    if not isinstance(
        history,
        pd.DataFrame,
    ):

        return pd.DataFrame()

    if history.empty:

        return pd.DataFrame()

    historical = history.copy()

    # ------------------------------------------------------
    # PREÇO
    # ------------------------------------------------------

    if "Close" in historical.columns:

        historical["price"] = pd.to_numeric(
            historical["Close"],
            errors="coerce",
        )

    elif "close" in historical.columns:

        historical["price"] = pd.to_numeric(
            historical["close"],
            errors="coerce",
        )

    elif "price" in historical.columns:

        historical["price"] = pd.to_numeric(
            historical["price"],
            errors="coerce",
        )

    else:

        return pd.DataFrame()

    # ------------------------------------------------------
    # MA21
    # ------------------------------------------------------

    if "ma21" not in historical.columns:

        historical["ma21"] = (
            historical["price"]
            .rolling(
                window=21,
                min_periods=21,
            )
            .mean()
        )

    # ------------------------------------------------------
    # MA200
    # ------------------------------------------------------

    if "ma200" not in historical.columns:

        historical["ma200"] = (
            historical["price"]
            .rolling(
                window=200,
                min_periods=200,
            )
            .mean()
        )

    # ------------------------------------------------------
    # RSI
    # ------------------------------------------------------

    if "rsi" not in historical.columns:

        delta = historical[
            "price"
        ].diff()

        gain = delta.clip(
            lower=0
        )

        loss = (
            -delta.clip(
                upper=0
            )
        )

        average_gain = gain.rolling(
            window=14,
            min_periods=14,
        ).mean()

        average_loss = loss.rolling(
            window=14,
            min_periods=14,
        ).mean()

        rs = average_gain / average_loss

        historical["rsi"] = (
            100
            - (
                100
                / (
                    1 + rs
                )
            )
        )

    historical = historical[
        [
            "price",
            "ma21",
            "ma200",
            "rsi",
        ]
    ].copy()

    historical = historical.dropna(
        subset=[
            "price",
            "ma21",
            "ma200",
            "rsi",
        ]
    )

    return historical


def build_analysis_data(
    price,
    indicators,
    historical_indicators,
):
    """
    Monta os dados enviados
    ao motor de análise.
    """

    return {

        "price":
            safe_float(
                price
            ),

        "rsi":
            safe_float(
                get_indicator_value(
                    indicators,
                    "rsi",
                )
            ),

        "ma21":
            safe_float(
                get_indicator_value(
                    indicators,
                    "ma21",
                )
            ),

        "ma200":
            safe_float(
                get_indicator_value(
                    indicators,
                    "ma200",
                )
            ),

        "volatility":
            safe_float(
                get_indicator_value(
                    indicators,
                    "volatility",
                )
            ),

        "historical":
            historical_indicators,
    }


def format_score(
    score,
):
    """
    Formata um Score para exibição.
    """

    score = safe_float(
        score
    )

    if score is None:
        return "N/D"

    return f"{score:.0f}/100"


def format_score_delta(
    variation,
):
    """
    Formata a variação histórica do Score.
    """

    variation = safe_float(
        variation
    )

    if variation is None:
        return None

    return f"{variation:+.0f} pts"


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
        help=(
            "Exemplos: PETR4, VALE3, ITUB4"
        ),
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
    # VALIDAÇÃO
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
                "Erro ao buscar os dados "
                "do mercado."
            )

            st.exception(
                error
            )

            st.stop()

    if market_data is None:

        st.error(
            f"Não foi possível obter "
            f"dados para {asset}."
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
            "Erro ao preparar os dados "
            "do mercado."
        )

        st.exception(
            error
        )

        st.stop()

    if prepared_data is None:

        st.error(
            "Os dados do mercado "
            "não puderam ser preparados."
        )

        st.stop()

    prepared_data = safe_dict(
        prepared_data
    )

    # ======================================================
    # HISTÓRICO DE MERCADO
    # ======================================================

    history = prepared_data.get(
        "history"
    )

    if not isinstance(
        history,
        pd.DataFrame,
    ):

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
    # PREÇO ATUAL
    # ======================================================

    try:

        price = get_current_price(
            prepared_data
        )

    except Exception:

        price = None

    price = safe_float(
        price
    )

    if price is None:

        # Fallback para o último Close.

        price_column = None

        for column in [
            "Close",
            "close",
            "price",
        ]:

            if column in history.columns:

                price_column = column
                break

        if price_column is not None:

            price = safe_float(
                history[
                    price_column
                ].dropna().iloc[-1]
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
                "os indicadores técnicos."
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

    indicators = safe_dict(
        indicators
    )

    # ======================================================
    # HISTÓRICO DE INDICADORES
    # ======================================================

    historical_indicators = (
        get_historical_indicators(
            indicators,
            prepared_data,
        )
    )

    # ======================================================
    # DADOS PARA ANÁLISE
    # ======================================================

    analysis_data = build_analysis_data(
        price,
        indicators,
        historical_indicators,
    )

    # ======================================================
    # VALIDAÇÃO DOS DADOS
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
    # MOTOR DE ANÁLISE
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
                "Erro ao executar "
                "a análise InvestIA."
            )

            st.exception(
                error
            )

            st.stop()

    result = safe_dict(
        result
    )

    if not result:

        st.error(
            "A análise não retornou resultado."
        )

        st.stop()

    # ======================================================
    # EXTRAÇÃO DOS RESULTADOS
    # ======================================================

    technical_score = get_analysis_value(
        result,
        "technical_score",
        "score",
    )

    fundamental_score = get_analysis_value(
        result,
        "fundamental_score",
        "score_fundamental",
    )

    integrated_score = get_analysis_value(
        result,
        "integrated_score",
    )

    classification = get_analysis_value(
        result,
        "classification",
        default="NEUTRO",
    )

    integrated_classification = get_analysis_value(
        result,
        "integrated_classification",
        default="SEM DADOS",
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
        default="Moderado",
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
        default="Indefinida",
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
        default="Sem dados",
    )

    reasons = get_analysis_value(
        result,
        "reasons",
        "justificativas",
        default=[],
    )

    if not isinstance(
        reasons,
        list,
    ):

        reasons = []

    breakdown = get_analysis_value(
        result,
        "breakdown",
        default={},
    )

    breakdown = safe_dict(
        breakdown
    )

    executive_summary = get_analysis_value(
        result,
        "executive_summary",
        default="",
    )

    # ======================================================
    # DADOS HISTÓRICOS DA ANÁLISE
    # ======================================================

    score_history = get_analysis_value(
        result,
        "score_history",
    )

    historical_summary = get_analysis_value(
        result,
        "historical_summary",
        default={},
    )

    historical_summary = safe_dict(
        historical_summary
    )

    score_evolution = get_analysis_value(
        result,
        "score_evolution",
        default="SEM DADOS",
    )

    score_variation = get_analysis_value(
        result,
        "score_variation",
    )

    score_consistency = get_analysis_value(
        result,
        "score_consistency",
        default="SEM DADOS",
    )

    signal_change = get_analysis_value(
        result,
        "signal_change",
        default={},
    )

    signal_change = safe_dict(
        signal_change
    )

    # ======================================================
    # CABEÇALHO DA ANÁLISE
    # ======================================================

    st.divider()

    st.header(
        f"📊 Análise do Ativo: {asset}"
    )

    st.caption(
        f"Sinal atual: {signal_icon} "
        f"{qualified_signal} "
        f"| Intensidade: {signal_level}"
    )

    # ======================================================
    # CARDS PRINCIPAIS
    # ======================================================

    price_col, tech_col, fund_col, integrated_col = (
        st.columns(
            4
        )
    )

    with price_col:

        st.metric(
            "Preço Atual",
            format_currency(
                price
            ),
        )

    with tech_col:

        tech_delta = format_score_delta(
            score_variation
        )

        st.metric(
            "Score Técnico",
            format_score(
                technical_score
            ),
            delta=tech_delta,
        )

    with fund_col:

        st.metric(
            "Score Fundamentalista",
            format_score(
                fundamental_score
            ),
        )

    with integrated_col:

        st.metric(
            "Score Integrado",
            format_score(
                integrated_score
            ),
        )

    # ======================================================
    # STATUS DA ANÁLISE
    # ======================================================

    status_col1, status_col2, status_col3, status_col4 = (
        st.columns(
            4
        )
    )

    with status_col1:

        st.metric(
            "Tendência",
            safe_text(
                trend,
                "Indefinida",
            ),
        )

    with status_col2:

        st.metric(
            "Risco",
            safe_text(
                risk,
                "Moderado",
            ),
        )

    with status_col3:

        st.metric(
            "Evolução do Score",
            safe_text(
                score_evolution,
                "SEM DADOS",
            ),
        )

    with status_col4:

        st.metric(
            "Consistência",
            safe_text(
                score_consistency,
                "SEM DADOS",
            ),
        )

    # ======================================================
    # CLASSIFICAÇÃO
    # ======================================================

    st.info(
        f"**Score Técnico:** {classification} "
        f"| **Score Integrado:** "
        f"{integrated_classification} "
        f"| **Recomendação:** {recommendation}"
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
    # COMPARAÇÃO DOS SCORES
    # ======================================================

    st.divider()

    st.subheader(
        "⚖️ Comparação dos Scores"
    )

    try:

        comparison_fig = (
            create_scores_comparison_chart(
                technical_score,
                fundamental_score,
                integrated_score,
            )
        )

        if comparison_fig is not None:

            st.plotly_chart(
                comparison_fig,
                use_container_width=True,
            )

        else:

            st.info(
                "Não há dados suficientes para "
                "comparar os Scores."
            )

    except Exception as error:

        st.warning(
            "Não foi possível gerar o gráfico "
            "de comparação dos Scores."
        )

        st.caption(
            str(error)
        )

    # ======================================================
    # INDICADORES ATUAIS
    # ======================================================

    st.divider()

    st.subheader(
        "📈 Indicadores Técnicos"
    )

    ma21 = safe_float(
        analysis_data.get(
            "ma21"
        )
    )

    ma200 = safe_float(
        analysis_data.get(
            "ma200"
        )
    )

    rsi = safe_float(
        analysis_data.get(
            "rsi"
        )
    )

    volatility = safe_float(
        analysis_data.get(
            "volatility"
        )
    )

    ind1, ind2, ind3, ind4 = st.columns(
        4
    )

    with ind1:

        st.metric(
            "MA21",
            format_currency(
                ma21
            )
            if ma21 is not None
            else "N/D",
        )

    with ind2:

        st.metric(
            "MA200",
            format_currency(
                ma200
            )
            if ma200 is not None
            else "N/D",
        )

    with ind3:

        st.metric(
            "RSI",
            f"{rsi:.2f}"
            if rsi is not None
            else "N/D",
        )

    with ind4:

        volatility_text = "N/D"

        if volatility is not None:

            volatility_text = (
                f"{volatility * 100:.2f}%"
            )

        st.metric(
            "Volatilidade",
            volatility_text,
        )

    # ======================================================
    # EVOLUÇÃO HISTÓRICA DO SCORE
    # ======================================================

    st.divider()

    st.subheader(
        "📈 Evolução Histórica do Score"
    )

    if isinstance(
        score_history,
        pd.DataFrame,
    ) and not score_history.empty:

        hist1, hist2, hist3, hist4 = st.columns(
            4
        )

        with hist1:

            current_historical_score = (
                historical_summary.get(
                    "current_score"
                )
            )

            st.metric(
                "Score Atual",
                format_score(
                    current_historical_score
                ),
            )

        with hist2:

            average_score = (
                historical_summary.get(
                    "average_score"
                )
            )

            st.metric(
                "Média do Período",
                format_score(
                    average_score
                ),
            )

        with hist3:

            maximum_score = (
                historical_summary.get(
                    "maximum_score"
                )
            )

            st.metric(
                "Score Máximo",
                format_score(
                    maximum_score
                ),
            )

        with hist4:

            minimum_score = (
                historical_summary.get(
                    "minimum_score"
                )
            )

            st.metric(
                "Score Mínimo",
                format_score(
                    minimum_score
                ),
            )

        try:

            score_fig = (
                create_score_evolution_chart(
                    score_history
                )
            )

            if score_fig is not None:

                st.plotly_chart(
                    score_fig,
                    use_container_width=True,
                )

        except Exception as error:

            st.warning(
                "Não foi possível gerar o gráfico "
                "de evolução do Score."
            )

            st.caption(
                str(error)
            )

        # ==================================================
        # MUDANÇA DE SINAL
        # ==================================================

        if signal_change:

            changed = signal_change.get(
                "changed",
                False,
            )

            previous_signal = safe_text(
                signal_change.get(
                    "previous"
                ),
                "N/D",
            )

            current_signal = safe_text(
                signal_change.get(
                    "current"
                ),
                qualified_signal,
            )

            if changed:

                st.warning(
                    f"⚡ Mudança de sinal identificada: "
                    f"**{previous_signal} → "
                    f"{current_signal}**"
                )

            else:

                st.caption(
                    f"Sinal permanece em "
                    f"**{current_signal}** no período analisado."
                )

    else:

        st.info(
            "Histórico de Score ainda não está "
            "disponível para este período."
        )

    # ======================================================
    # PREÇO E MÉDIAS MÓVEIS
    # ======================================================

    st.divider()

    st.subheader(
        "📉 Evolução do Preço e Médias"
    )

    try:

        indicators_fig = (
            create_price_indicators_chart(
                historical_indicators
            )
        )

        if indicators_fig is not None:

            st.plotly_chart(
                indicators_fig,
                use_container_width=True,
            )

        else:

            price_fig = create_price_chart(
                history
            )

            if price_fig is not None:

                st.plotly_chart(
                    price_fig,
                    use_container_width=True,
                )

            else:

                st.info(
                    "Não foi possível gerar o "
                    "histórico de preço."
                )

    except Exception as error:

        st.warning(
            "Não foi possível gerar o gráfico "
            "de preço e médias."
        )

        st.caption(
            str(error)
        )

    # ======================================================
    # ANÁLISE INTEGRADA
    # ======================================================

    st.divider()

    st.subheader(
        "📊 Análise Histórica Integrada"
    )

    if (
        isinstance(
            historical_indicators,
            pd.DataFrame,
        )
        and not historical_indicators.empty
        and isinstance(
            score_history,
            pd.DataFrame,
        )
        and not score_history.empty
    ):

        try:

            integrated_fig = (
                create_integrated_analysis_chart(
                    historical_indicators,
                    score_history,
                )
            )

            if integrated_fig is not None:

                st.plotly_chart(
                    integrated_fig,
                    use_container_width=True,
                )

        except Exception as error:

            st.warning(
                "Não foi possível gerar a análise "
                "histórica integrada."
            )

            st.caption(
                str(error)
            )

    else:

        st.info(
            "Dados históricos insuficientes "
            "para a análise integrada."
        )

    # ======================================================
    # COMPOSIÇÃO DO SCORE
    # ======================================================

    st.divider()

    st.subheader(
        "🧠 Composição do Score Técnico"
    )

    base_points = safe_float(
        breakdown.get(
            "base"
        ),
        50,
    )

    raw_score = safe_float(
        breakdown.get(
            "raw_score"
        )
    )

    st.caption(
        "O Score Técnico parte de uma base de "
        "50 pontos e é ajustado conforme MA21, "
        "MA200 e RSI."
    )

    st.write(
        f"**Base inicial:** {base_points:.0f} pontos"
    )

    breakdown_col1, breakdown_col2, breakdown_col3 = (
        st.columns(
            3
        )
    )

    breakdown_items = [

        (
            breakdown_col1,
            "📏 MA21",
            "ma21",
        ),

        (
            breakdown_col2,
            "📐 MA200",
            "ma200",
        ),

        (
            breakdown_col3,
            "📊 RSI",
            "rsi",
        ),

    ]

    for column, title, key in breakdown_items:

        with column:

            item = safe_dict(
                breakdown.get(
                    key
                )
            )

            points = safe_float(
                item.get(
                    "points"
                ),
                0,
            )

            item_signal = safe_text(
                item.get(
                    "signal"
                ),
                "Neutro",
            )

            item_reason = safe_text(
                item.get(
                    "reason"
                ),
                "Sem informação.",
            )

            st.markdown(
                f"### {title}"
            )

            st.metric(
                "Contribuição",
                f"{points:+.0f} pts",
            )

            st.write(
                f"**Sinal:** {item_signal}"
            )

            st.caption(
                item_reason
            )

    if raw_score is not None:

        st.success(
            f"**Score Técnico Final: "
            f"{format_score(technical_score)}** "
            f"| Cálculo bruto: "
            f"{raw_score:.0f}"
        )

    else:

        st.success(
            f"**Score Técnico Final: "
            f"{format_score(technical_score)}**"
        )

    # ======================================================
    # FUNDAMENTAÇÃO
    # ======================================================

    st.divider()

    st.subheader(
        "🔎 Fundamentação da Análise"
    )

    analysis_col1, analysis_col2 = st.columns(
        2
    )

    with analysis_col1:

        st.markdown(
            "### Indicadores e Tendência"
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
            "### 🛡️ Gestão de Risco"
        )

        st.write(
            f"{risk_icon(risk)} **{risk}**"
        )

        st.write(
            f"**Score Técnico:** "
            f"{format_score(technical_score)}"
        )

        st.write(
            f"**Score Fundamentalista:** "
            f"{format_score(fundamental_score)}"
        )

        st.write(
            f"**Score Integrado:** "
            f"{format_score(integrated_score)}"
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

    summary_col1, summary_col2 = st.columns(
        2
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
            f"**Score Técnico:** "
            f"{format_score(technical_score)}"
        )

        st.write(
            f"**Score Fundamentalista:** "
            f"{format_score(fundamental_score)}"
        )

        st.write(
            f"**Score Integrado:** "
            f"{format_score(integrated_score)}"
        )

    with summary_col2:

        st.write(
            f"**Classificação Técnica:** "
            f"{classification}"
        )

        st.write(
            f"**Classificação Integrada:** "
            f"{integrated_classification}"
        )

        st.write(
            f"**Evolução do Score:** "
            f"{score_evolution}"
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
# TELA INICIAL
# ==========================================================

else:

    st.info(
        "Digite o código de um ativo e clique em "
        "**🔎 Analisar ativo**."
    )

    st.markdown(
        """
### Como utilizar

1. Informe o código do ativo.
2. Escolha o período de análise.
3. Clique em **Analisar ativo**.
4. Analise o **Score Técnico**.
5. Consulte o **Score Fundamentalista**, quando disponível.
6. Avalie o **Score Integrado**.
7. Observe a evolução histórica do Score.
8. Compare o preço com as médias MA21 e MA200.

**Exemplos de ativos brasileiros:**

- PETR4
- VALE3
- ITUB4
- BBAS3
- WEGE3
"""
    )
