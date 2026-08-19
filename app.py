"""
InvestIA PRO
Aplicação principal

Versão: v0.6
Fase: 2.9.5 - Integração da Validação dos Indicadores
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

            return result[key]

    return default


def get_validation_info(
    result,
):
    """
    Extrai informações de validação
    retornadas pelo analysis.py.
    """

    if not isinstance(
        result,
        dict,
    ):

        return {
            "valid": False,
            "status": "INCONSISTENTE",
            "icon": "🔴",
            "message":
                "Resultado da análise inválido.",
        }

    validation = result.get(
        "validation",
        {},
    )

    if not isinstance(
        validation,
        dict,
    ):

        validation = {}

    valid = result.get(
        "analysis_valid",
        result.get(
            "valid",
            validation.get(
                "valid",
                False,
            ),
        ),
    )

    status = result.get(
        "data_status",
        validation.get(
            "status",
            "INCONSISTENTE",
        ),
    )

    icon = result.get(
        "data_status_icon",
        validation.get(
            "status_icon",
            "🔴",
        ),
    )

    message = result.get(
        "message",
        validation.get(
            "message",
            "Status dos dados não informado.",
        ),
    )

    return {
        "valid": bool(valid),
        "status": str(status),
        "icon": str(icon),
        "message": str(message),
    }


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
    # VALIDAÇÃO DO ATIVO
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
                "Erro ao buscar os dados "
                "do mercado."
            )

            st.exception(
                error
            )

            st.stop()

    # ======================================================
    # VALIDAÇÃO DO RETORNO DO MERCADO
    # ======================================================

    if market_data is None:

        st.error(
            f"Não foi possível obter "
            f"dados para {asset}."
        )

        st.stop()

    # ======================================================
    # PREPARAÇÃO
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

    if not isinstance(
        prepared_data,
        dict,
    ):

        st.error(
            "O módulo de mercado retornou "
            "uma estrutura inválida."
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

    except Exception as error:

        st.error(
            "Erro ao determinar "
            "o preço atual."
        )

        st.exception(
            error
        )

        st.stop()

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

    if not isinstance(
        indicators,
        dict,
    ):

        st.error(
            "O módulo de indicadores retornou "
            "uma estrutura inválida."
        )

        st.stop()

    # ======================================================
    # EXTRAÇÃO DOS INDICADORES
    # ======================================================

    ma21 = get_indicator_value(
        indicators,
        "ma21",
    )

    ma200 = get_indicator_value(
        indicators,
        "ma200",
    )

    rsi = get_indicator_value(
        indicators,
        "rsi",
    )

    volatility = get_indicator_value(
        indicators,
        "volatility",
    )

    # ======================================================
    # DADOS PARA ANÁLISE
    # ======================================================

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

    # ======================================================
    # VALIDAÇÃO BÁSICA
    # ======================================================

    try:

        basic_validation = validate_analysis_data(
            analysis_data
        )

    except Exception:

        basic_validation = True

    if not basic_validation:

        st.warning(
            "Os dados técnicos retornados "
            "são insuficientes para uma "
            "análise completa."
        )

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
            "uma estrutura inválida."
        )

        st.stop()

    # ======================================================
    # STATUS DOS DADOS
    # ======================================================

    validation_info = get_validation_info(
        result
    )

    validation_status = validation_info[
        "status"
    ]

    validation_icon = validation_info[
        "icon"
    ]

    validation_message = validation_info[
        "message"
    ]

    # ======================================================
    # INDICADOR DE QUALIDADE DOS DADOS
    # ======================================================

    st.divider()

    st.subheader(
        "🔎 Qualidade dos dados"
    )

    quality_col1, quality_col2 = st.columns(
        [1, 4]
    )

    with quality_col1:

        st.metric(
            "Status",
            f"{validation_icon} "
            f"{validation_status}",
        )

    with quality_col2:

        if validation_status == "CONSISTENTE":

            st.success(
                validation_message
            )

        elif validation_status == "INCOMPLETO":

            st.warning(
                validation_message
            )

        else:

            st.error(
                validation_message
            )

    # ======================================================
    # EXTRAÇÃO DOS RESULTADOS
    # ======================================================

    score = get_analysis_value(
        result,
        "score",
        default=None,
    )

    classification = get_analysis_value(
        result,
        "classification",
        default="INDISPONÍVEL",
    )

    signal = get_analysis_value(
        result,
        "signal",
        default="INDEFINIDO",
    )

    qualified_signal = get_analysis_value(
        result,
        "qualified_signal",
        default=signal,
    )

    signal_level = get_analysis_value(
        result,
        "signal_level",
        default="Indisponível",
    )

    signal_icon = get_analysis_value(
        result,
        "signal_icon",
        default="⚪",
    )

    trend = get_analysis_value(
        result,
        "trend",
        "tendencia",
        default="Indeterminada",
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
        default="Indeterminado",
    )

    rsi_status = get_analysis_value(
        result,
        "rsi_status",
        default="Indisponível",
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

    analysis_valid = get_analysis_value(
        result,
        "analysis_valid",
        "valid",
        default=False,
    )

    # ======================================================
    # CABEÇALHO DA ANÁLISE
    # ======================================================

    st.divider()

    st.header(
        f"📊 Análise do ativo: {asset}"
    )

    # ======================================================
    # ALERTA PARA DADOS NÃO CONSISTENTES
    # ======================================================

    if not analysis_valid:

        st.warning(
            "A análise técnica não está "
            "disponível com confiabilidade suficiente. "
            "O sistema não irá gerar uma recomendação "
            "baseada em dados incompletos ou inválidos."
        )

        st.info(
            f"Motivo: {validation_message}"
        )

        # --------------------------------------------------
        # MOSTRA O QUE ESTÁ DISPONÍVEL
        # --------------------------------------------------

        available_col1, available_col2 = st.columns(
            2
        )

        with available_col1:

            st.write(
                f"**Ativo:** {asset}"
            )

            st.write(
                f"**Preço:** "
                f"{format_currency(price)}"
            )

        with available_col2:

            st.write(
                f"**Status:** "
                f"{validation_icon} "
                f"{validation_status}"
            )

            st.write(
                f"**Recomendação:** "
                f"{recommendation}"
            )

        # Não interrompe a página.
        # O gráfico e os dados disponíveis
        # continuam sendo apresentados.

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

        if score is None:

            st.metric(
                "Score InvestIA",
                "N/D",
            )

        else:

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
    # CLASSIFICAÇÃO E SINAL
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

        if analysis_valid:

            st.success(
                executive_summary
            )

        else:

            st.warning(
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

        if ma21 is None:

            st.metric(
                "MA21",
                "N/D",
            )

        else:

            st.metric(
                "MA21",
                format_currency(
                    ma21
                ),
            )

    with ind2:

        if ma200 is None:

            st.metric(
                "MA200",
                "N/D",
            )

        else:

            st.metric(
                "MA200",
                format_currency(
                    ma200
                ),
            )

    with ind3:

        if rsi is None:

            st.metric(
                "RSI",
                "N/D",
            )

        else:

            st.metric(
                "RSI",
                f"{float(rsi):.2f}",
            )

    with ind4:

        if volatility is None:

            st.metric(
                "Volatilidade",
                "N/D",
            )

        else:

            try:

                volatility_percent = (
                    float(volatility)
                    * 100
                )

                st.metric(
                    "Volatilidade",
                    f"{volatility_percent:.2f}%",
                )

            except (
                TypeError,
                ValueError,
            ):

                st.metric(
                    "Volatilidade",
                    "N/D",
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

    # ======================================================
    # SCORE DISPONÍVEL
    # ======================================================

    if not isinstance(
        breakdown,
        dict,
    ):

        breakdown = {}

    base_points = breakdown.get(
        "base",
        50,
    )

    try:

        base_points = int(
            base_points
        )

    except (
        TypeError,
        ValueError,
    ):

        base_points = 50

    st.write(
        f"**Base:** "
        f"{base_points:+d} pontos"
    )

    # ======================================================
    # COMPONENTES
    # ======================================================

    bd1, bd2, bd3 = st.columns(
        3
    )

    # ======================================================
    # MA21
    # ======================================================

    with bd1:

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

        try:

            ma21_points = int(
                ma21_points
            )

        except (
            TypeError,
            ValueError,
        ):

            ma21_points = 0

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

        try:

            ma200_points = int(
                ma200_points
            )

        except (
            TypeError,
            ValueError,
        ):

            ma200_points = 0

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

        try:

            rsi_points = int(
                rsi_points
            )

        except (
            TypeError,
            ValueError,
        ):

            rsi_points = 0

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

    raw_score = breakdown.get(
        "raw_score"
    )

    if score is None:

        st.warning(
            "**Score final:** indisponível."
        )

    elif raw_score is not None:

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
    # JUSTIFICATIVAS
    # ======================================================

    with analysis_col1:

        st.markdown(
            "### Fundamentação"
        )

        if reasons:

            if isinstance(
                reasons,
                list,
            ):

                for reason in reasons:

                    st.write(
                        f"✔ {reason}"
                    )

            else:

                st.write(
                    f"✔ {reasons}"
                )

        else:

            st.info(
                "Nenhuma justificativa "
                "foi retornada."
            )

    # ======================================================
    # RISCO
    # ======================================================

    with analysis_col2:

        st.markdown(
            "### 🛡️ Gestão de risco"
        )

        try:

            icon = risk_icon(
                risk
            )

        except Exception:

            icon = "🛡️"

        st.write(
            f"{icon} **{risk}**"
        )

        if score is not None:

            st.write(
                f"**Score:** {score}/100"
            )

        else:

            st.write(
                "**Score:** N/D"
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

        if score is not None:

            st.write(
                f"**Score:** {score}/100"
            )

        else:

            st.write(
                "**Score:** N/D"
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

        try:

            summary_risk_icon = risk_icon(
                risk
            )

        except Exception:

            summary_risk_icon = "🛡️"

        st.write(
            f"**Risco:** "
            f"{summary_risk_icon} {risk}"
        )

        st.write(
            f"**Recomendação:** "
            f"{recommendation}"
        )

        st.write(
            f"**Dados:** "
            f"{validation_icon} "
            f"{validation_status}"
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

**Exemplos:** PETR4, VALE3, ITUB4.
"""
    )
