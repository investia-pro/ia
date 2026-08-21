"""
InvestIA PRO
Aplicação Principal

Versão: v0.7
Fase: 3.0.4 - Consenso e Confiança da Análise
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


def get_dict_value(
    data,
    *keys,
    default=None,
):
    """
    Obtém um valor de um dicionário
    aceitando nomes alternativos.
    """

    if not isinstance(
        data,
        dict,
    ):

        return default

    for key in keys:

        if key in data:

            value = data.get(
                key
            )

            if value is not None:

                return value

    return default


def safe_float(
    value,
    default=None,
):
    """
    Converte um valor para float
    com segurança.
    """

    if value is None:

        return default

    try:

        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return default


def format_score(
    score,
):
    """
    Formata Score para apresentação.
    """

    score = safe_float(
        score
    )

    if score is None:

        return "N/D"

    return f"{score:.0f}/100"


def format_percent(
    value,
    decimals=1,
):
    """
    Formata decimal como percentual.
    """

    value = safe_float(
        value
    )

    if value is None:

        return "N/D"

    return (
        f"{value * 100:.{decimals}f}%"
    )


def consensus_icon(
    consensus,
):
    """
    Retorna ícone conforme o consenso.
    """

    consensus = (
        str(consensus)
        .strip()
        .upper()
    )

    icons = {

        "FORTE": "🟢",

        "MODERADO": "🟡",

        "FRACO": "🟠",

        "DIVERGENTE": "🔴",

        "NÃO AVALIADO": "⚪",

    }

    return icons.get(
        consensus,
        "⚪",
    )


def confidence_icon(
    confidence,
):
    """
    Retorna ícone conforme a confiança.
    """

    confidence = (
        str(confidence)
        .strip()
        .upper()
    )

    icons = {

        "ALTA": "🟢",

        "MÉDIA-ALTA": "🟢",

        "MÉDIA": "🟡",

        "BAIXA": "🔴",

    }

    return icons.get(
        confidence,
        "⚪",
    )


def score_delta(
    current_score,
    reference_score,
):
    """
    Calcula a diferença entre dois Scores.
    """

    current_score = safe_float(
        current_score
    )

    reference_score = safe_float(
        reference_score
    )

    if (
        current_score is None
        or reference_score is None
    ):

        return None

    return current_score - reference_score


# ==========================================================
# CABEÇALHO
# ==========================================================

st.title(
    "📈 InvestIA PRO"
)

st.caption(
    "Análise integrada de ativos: "
    "Técnica + Fundamentalista + Consenso"
)


# ==========================================================
# ENTRADA DO USUÁRIO
# ==========================================================

input_col, period_col = st.columns(
    [3, 1]
)


with input_col:

    asset_input = st.text_input(
        "Digite o código do ativo",
        value="PETR4",
        max_chars=20,
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
        asset_input
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
                "Erro ao buscar os dados "
                "do mercado."
            )

            st.exception(
                error
            )

            st.stop()

    # ======================================================
    # VALIDAÇÃO DO RETORNO
    # ======================================================

    if market_data is None:

        st.error(
            f"Não foi possível obter "
            f"dados para {asset}."
        )

        st.stop()

    # ======================================================
    # PREPARAÇÃO DOS DADOS
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
            "Os dados do mercado não puderam "
            "ser preparados."
        )

        st.stop()

    # ======================================================
    # HISTÓRICO
    # ======================================================

    history = get_dict_value(
        prepared_data,
        "history",
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

    price = get_current_price(
        prepared_data
    )

    price = safe_float(
        price
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

    if not isinstance(
        indicators,
        dict,
    ):

        st.error(
            "Os indicadores técnicos "
            "não foram calculados corretamente."
        )

        st.stop()

    # ======================================================
    # DADOS FUNDAMENTALISTAS
    # ======================================================

    fundamentals = get_dict_value(
        prepared_data,
        "fundamentals",
        default={},
    )

    if not isinstance(
        fundamentals,
        dict,
    ):

        fundamentals = {}

    # ======================================================
    # DADOS PARA ANÁLISE
    # ======================================================

    analysis_data = {

        # --------------------------------------------------
        # DADOS TÉCNICOS
        # --------------------------------------------------

        "price":
            price,

        "ma21":
            get_dict_value(
                indicators,
                "ma21",
            ),

        "ma200":
            get_dict_value(
                indicators,
                "ma200",
            ),

        "rsi":
            get_dict_value(
                indicators,
                "rsi",
            ),

        "volatility":
            get_dict_value(
                indicators,
                "volatility",
                default=0,
            ),

        # --------------------------------------------------
        # FUNDAMENTOS
        # --------------------------------------------------

        "fundamentals":
            fundamentals,
    }

    # ======================================================
    # VALIDAÇÃO DOS DADOS TÉCNICOS
    # ======================================================

    technical_validation_data = {

        "price":
            analysis_data["price"],

        "ma21":
            analysis_data["ma21"],

        "ma200":
            analysis_data["ma200"],

        "rsi":
            analysis_data["rsi"],
    }

    if not validate_analysis_data(
        technical_validation_data
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
        "Executando análise integrada InvestIA..."
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

    if not isinstance(
        result,
        dict,
    ):

        st.error(
            "A análise retornou "
            "um resultado inválido."
        )

        st.stop()

    # ======================================================
    # EXTRAÇÃO DOS SCORES
    # ======================================================

    technical_score = get_dict_value(
        result,
        "technical_score",
        default=0,
    )

    fundamental_score = get_dict_value(
        result,
        "fundamental_score",
        default=None,
    )

    integrated_score = get_dict_value(
        result,
        "integrated_score",
        "score",
        default=0,
    )

    # ======================================================
    # CLASSIFICAÇÕES
    # ======================================================

    technical_classification = get_dict_value(
        result,
        "technical_classification",
        default="N/D",
    )

    fundamental_classification = get_dict_value(
        result,
        "fundamental_classification",
        default="N/D",
    )

    integrated_classification = get_dict_value(
        result,
        "integrated_classification",
        "classification",
        default="N/D",
    )

    # ======================================================
    # SINAIS
    # ======================================================

    technical_signal = get_dict_value(
        result,
        "technical_signal",
        default="N/D",
    )

    fundamental_signal = get_dict_value(
        result,
        "fundamental_signal",
        default="N/D",
    )

    integrated_signal = get_dict_value(
        result,
        "integrated_signal",
        "signal",
        default="N/D",
    )

    qualified_signal = get_dict_value(
        result,
        "qualified_signal",
        default=integrated_signal,
    )

    signal_level = get_dict_value(
        result,
        "signal_level",
        default="N/D",
    )

    signal_icon = get_dict_value(
        result,
        "signal_icon",
        default="⚪",
    )

    # ======================================================
    # FUNDAMENTOS
    # ======================================================

    fundamental_status = get_dict_value(
        result,
        "fundamental_status",
        default="Indisponível",
    )

    fundamental_completeness = get_dict_value(
        result,
        "fundamental_completeness",
        default=0,
    )

    # ======================================================
    # CONSENSO
    # ======================================================

    consensus = get_dict_value(
        result,
        "consensus",
        default="NÃO AVALIADO",
    )

    divergence = get_dict_value(
        result,
        "divergence",
        default=None,
    )

    consensus_reason = get_dict_value(
        result,
        "consensus_reason",
        default="Informação não disponível.",
    )

    # ======================================================
    # CONFIANÇA
    # ======================================================

    confidence = get_dict_value(
        result,
        "confidence",
        default="MÉDIA",
    )

    confidence_score = get_dict_value(
        result,
        "confidence_score",
        default=50,
    )

    confidence_reason = get_dict_value(
        result,
        "confidence_reason",
        default="Informação não disponível.",
    )

    # ======================================================
    # ANÁLISE GERAL
    # ======================================================

    trend = get_dict_value(
        result,
        "trend",
        "tendencia",
        default="Indefinida",
    )

    rsi_status = get_dict_value(
        result,
        "rsi_status",
        default="Indisponível",
    )

    recommendation = get_dict_value(
        result,
        "recommendation",
        "recomendacao",
        default="AGUARDAR",
    )

    risk = get_dict_value(
        result,
        "risk",
        "risco",
        default="Moderado",
    )

    reasons = get_dict_value(
        result,
        "reasons",
        "justificativas",
        default=[],
    )

    executive_summary = get_dict_value(
        result,
        "executive_summary",
        default="",
    )

    # ======================================================
    # BREAKDOWNS
    # ======================================================

    technical_breakdown = get_dict_value(
        result,
        "technical_breakdown",
        "breakdown",
        default={},
    )

    fundamental_breakdown = get_dict_value(
        result,
        "fundamental_breakdown",
        default={},
    )

    integrated_breakdown = get_dict_value(
        result,
        "integrated_breakdown",
        default={},
    )

    # ======================================================
    # CABEÇALHO DA ANÁLISE
    # ======================================================

    st.divider()

    st.header(
        f"📊 Análise Integrada: {asset}"
    )

    # ======================================================
    # PREÇO E RECOMENDAÇÃO
    # ======================================================

    top1, top2, top3, top4 = st.columns(
        4
    )

    with top1:

        st.metric(
            "Preço Atual",
            format_currency(
                price
            ),
        )

    with top2:

        st.metric(
            "Score Integrado",
            format_score(
                integrated_score
            ),
        )

    with top3:

        st.metric(
            "Tendência",
            str(trend),
        )

    with top4:

        st.metric(
            "Recomendação",
            str(recommendation),
        )

    # ======================================================
    # SINAL PRINCIPAL
    # ======================================================

    st.info(
        f"**Sinal:** {qualified_signal} "
        f"| **Nível:** "
        f"{signal_icon} {signal_level} "
        f"| **Classificação:** "
        f"{integrated_classification}"
    )

    # ======================================================
    # OS TRÊS SCORES
    # ======================================================

    st.divider()

    st.subheader(
        "🧠 Scores InvestIA"
    )

    score1, score2, score3 = st.columns(
        3
    )

    with score1:

        st.metric(
            "Score Técnico",
            format_score(
                technical_score
            ),
        )

        st.caption(
            f"Classificação: "
            f"{technical_classification}"
        )

        st.caption(
            f"Sinal: "
            f"{technical_signal}"
        )

    with score2:

        st.metric(
            "Score Fundamentalista",
            format_score(
                fundamental_score
            ),
        )

        st.caption(
            f"Classificação: "
            f"{fundamental_classification}"
        )

        st.caption(
            f"Sinal: "
            f"{fundamental_signal}"
        )

        st.caption(
            f"Status: "
            f"{fundamental_status}"
        )

    with score3:

        st.metric(
            "Score Integrado",
            format_score(
                integrated_score
            ),
        )

        st.caption(
            f"Classificação: "
            f"{integrated_classification}"
        )

        st.caption(
            f"Sinal: "
            f"{integrated_signal}"
        )

    # ======================================================
    # PAINEL DE QUALIDADE
    # ======================================================

    st.divider()

    st.subheader(
        "🎯 Qualidade da Análise"
    )

    quality1, quality2, quality3, quality4 = (
        st.columns(
            4
        )
    )

    with quality1:

        divergence_value = safe_float(
            divergence
        )

        divergence_text = (
            f"{divergence_value:.1f} pts"
            if divergence_value is not None
            else "N/D"
        )

        st.metric(
            "Divergência",
            divergence_text,
        )

    with quality2:

        st.metric(
            "Consenso",
            f"{consensus_icon(consensus)} "
            f"{consensus}",
        )

    with quality3:

        st.metric(
            "Confiança",
            f"{confidence_icon(confidence)} "
            f"{confidence}",
        )

    with quality4:

        confidence_value = safe_float(
            confidence_score,
            default=0,
        )

        st.metric(
            "Score de Confiança",
            f"{confidence_value:.0f}/100",
        )

    # ======================================================
    # INTERPRETAÇÃO DA QUALIDADE
    # ======================================================

    quality_col1, quality_col2 = st.columns(
        2
    )

    with quality_col1:

        st.markdown(
            "#### Consenso entre os modelos"
        )

        st.write(
            consensus_reason
        )

    with quality_col2:

        st.markdown(
            "#### Confiabilidade da análise"
        )

        st.write(
            confidence_reason
        )

    # ======================================================
    # METODOLOGIA DO SCORE INTEGRADO
    # ======================================================

    st.divider()

    st.subheader(
        "⚙️ Composição do Score Integrado"
    )

    integrated_technical = get_dict_value(
        integrated_breakdown,
        "technical",
        default={},
    )

    integrated_fundamental = get_dict_value(
        integrated_breakdown,
        "fundamental",
        default={},
    )

    integrated_data = get_dict_value(
        integrated_breakdown,
        "integrated",
        default={},
    )

    technical_weight = get_dict_value(
        integrated_technical,
        "weight",
        default=1.0,
    )

    fundamental_weight = get_dict_value(
        integrated_fundamental,
        "weight",
        default=0.0,
    )

    integration_method = get_dict_value(
        integrated_data,
        "method",
        default="Método não informado.",
    )

    weight1, weight2, weight3 = st.columns(
        3
    )

    with weight1:

        st.metric(
            "Peso Técnico",
            format_percent(
                technical_weight
            ),
        )

    with weight2:

        st.metric(
            "Peso Fundamentalista",
            format_percent(
                fundamental_weight
            ),
        )

    with weight3:

        st.metric(
            "Cobertura Fundamentalista",
            format_percent(
                fundamental_completeness
            ),
        )

    st.caption(
        f"**Método:** {integration_method}"
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

    indicator1, indicator2, indicator3, indicator4 = (
        st.columns(
            4
        )
    )

    with indicator1:

        st.metric(
            "MA21",
            format_currency(
                analysis_data[
                    "ma21"
                ]
            ),
        )

    with indicator2:

        st.metric(
            "MA200",
            format_currency(
                analysis_data[
                    "ma200"
                ]
            ),
        )

    with indicator3:

        rsi_value = safe_float(
            analysis_data[
                "rsi"
            ]
        )

        st.metric(
            "RSI",
            (
                f"{rsi_value:.2f}"
                if rsi_value is not None
                else "N/D"
            ),
        )

    with indicator4:

        volatility_value = safe_float(
            analysis_data[
                "volatility"
            ],
            default=0,
        )

        st.metric(
            "Volatilidade",
            f"{volatility_value * 100:.2f}%",
        )

    st.caption(
        f"Status do RSI: {rsi_status}"
    )

    # ======================================================
    # BREAKDOWN TÉCNICO
    # ======================================================

    st.divider()

    st.subheader(
        "📊 Composição do Score Técnico"
    )

    if isinstance(
        technical_breakdown,
        dict,
    ):

        base_points = get_dict_value(
            technical_breakdown,
            "base",
            default=50,
        )

        raw_score = get_dict_value(
            technical_breakdown,
            "raw_score",
            default=None,
        )

        st.write(
            f"**Base do Score:** "
            f"{base_points} pontos"
        )

        tech1, tech2, tech3 = st.columns(
            3
        )

        # --------------------------------------------------
        # MA21
        # --------------------------------------------------

        with tech1:

            ma21_data = get_dict_value(
                technical_breakdown,
                "ma21",
                default={},
            )

            st.markdown(
                "### 📏 MA21"
            )

            st.metric(
                "Contribuição",
                (
                    f"{safe_float(get_dict_value(ma21_data, 'points', default=0), 0):+.0f} pts"
                ),
            )

            st.write(
                f"**Sinal:** "
                f"{get_dict_value(ma21_data, 'signal', default='Neutro')}"
            )

            st.caption(
                get_dict_value(
                    ma21_data,
                    "reason",
                    default="Sem informação.",
                )
            )

        # --------------------------------------------------
        # MA200
        # --------------------------------------------------

        with tech2:

            ma200_data = get_dict_value(
                technical_breakdown,
                "ma200",
                default={},
            )

            st.markdown(
                "### 📐 MA200"
            )

            st.metric(
                "Contribuição",
                (
                    f"{safe_float(get_dict_value(ma200_data, 'points', default=0), 0):+.0f} pts"
                ),
            )

            st.write(
                f"**Sinal:** "
                f"{get_dict_value(ma200_data, 'signal', default='Neutro')}"
            )

            st.caption(
                get_dict_value(
                    ma200_data,
                    "reason",
                    default="Sem informação.",
                )
            )

        # --------------------------------------------------
        # RSI
        # --------------------------------------------------

        with tech3:

            rsi_data = get_dict_value(
                technical_breakdown,
                "rsi",
                default={},
            )

            st.markdown(
                "### 📊 RSI"
            )

            st.metric(
                "Contribuição",
                (
                    f"{safe_float(get_dict_value(rsi_data, 'points', default=0), 0):+.0f} pts"
                ),
            )

            st.write(
                f"**Sinal:** "
                f"{get_dict_value(rsi_data, 'signal', default='Neutro')}"
            )

            st.caption(
                get_dict_value(
                    rsi_data,
                    "reason",
                    default="Sem informação.",
                )
            )

        if raw_score is not None:

            st.success(
                f"**Score Técnico Final:** "
                f"{format_score(technical_score)} "
                f"| Cálculo bruto: {raw_score}"
            )

        else:

            st.success(
                f"**Score Técnico Final:** "
                f"{format_score(technical_score)}"
            )

    else:

        st.info(
            "Detalhamento técnico não disponível."
        )

    # ======================================================
    # BREAKDOWN FUNDAMENTALISTA
    # ======================================================

    st.divider()

    st.subheader(
        "🏢 Análise Fundamentalista"
    )

    if fundamental_score is None:

        st.warning(
            "Os dados fundamentalistas não estão "
            "disponíveis para este ativo."
        )

    else:

        fundamental_cols = st.columns(
            3
        )

        with fundamental_cols[0]:

            st.metric(
                "Score Fundamentalista",
                format_score(
                    fundamental_score
                ),
            )

        with fundamental_cols[1]:

            st.metric(
                "Status dos Dados",
                str(
                    fundamental_status
                ),
            )

        with fundamental_cols[2]:

            st.metric(
                "Cobertura",
                format_percent(
                    fundamental_completeness
                ),
            )

        if fundamental_breakdown:

            st.caption(
                "Detalhamento dos fundamentos "
                "utilizados no Score:"
            )

            st.write(
                fundamental_breakdown
            )

    # ======================================================
    # GRÁFICO
    # ======================================================

    st.divider()

    st.subheader(
        "📈 Evolução do Preço"
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
    # ANÁLISE DETALHADA
    # ======================================================

    st.divider()

    st.subheader(
        "🔎 Análise Detalhada"
    )

    analysis_col1, analysis_col2 = st.columns(
        2
    )

    # ======================================================
    # FUNDAMENTAÇÃO
    # ======================================================

    with analysis_col1:

        st.markdown(
            "### Fundamentação"
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
                "Nenhuma justificativa "
                "foi retornada."
            )

    # ======================================================
    # GESTÃO DE RISCO
    # ======================================================

    with analysis_col2:

        st.markdown(
            "### 🛡️ Gestão de Risco"
        )

        st.write(
            f"{risk_icon(risk)} **{risk}**"
        )

        st.write(
            f"**Score Integrado:** "
            f"{format_score(integrated_score)}"
        )

        st.write(
            f"**Consenso:** "
            f"{consensus_icon(consensus)} "
            f"{consensus}"
        )

        st.write(
            f"**Confiança:** "
            f"{confidence_icon(confidence)} "
            f"{confidence}"
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
            f"**Recomendação:** "
            f"{recommendation}"
        )

    # ======================================================
    # RESUMO FINAL
    # ======================================================

    st.divider()

    st.subheader(
        "📋 Resumo da Análise"
    )

    summary_col1, summary_col2, summary_col3 = (
        st.columns(
            3
        )
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

    with summary_col2:

        st.write(
            f"**Score Fundamentalista:** "
            f"{format_score(fundamental_score)}"
        )

        st.write(
            f"**Score Integrado:** "
            f"{format_score(integrated_score)}"
        )

        st.write(
            f"**Consenso:** "
            f"{consensus}"
        )

    with summary_col3:

        st.write(
            f"**Confiança:** "
            f"{confidence}"
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
        "Digite um ativo e clique em "
        "🔎 Analisar ativo."
    )

    st.markdown(
        """
### Como funciona a análise

1. Informe o código do ativo.
2. Escolha o período de análise.
3. Clique em **Analisar ativo**.
4. O InvestIA calcula o Score Técnico.
5. Os fundamentos disponíveis são avaliados.
6. É calculado o Score Fundamentalista.
7. Os modelos são integrados em um Score Final.
8. O sistema mede a divergência e o consenso.
9. A confiança da análise ajusta a recomendação.

### Exemplo de interpretação

- **Score Técnico alto + Fundamentalista alto:** maior convergência.
- **Scores próximos:** maior consenso.
- **Scores muito diferentes:** análise divergente.
- **Baixa cobertura fundamentalista:** maior peso para o técnico.

**Exemplos de ativos:** PETR4, VALE3, ITUB4.
"""
    )
