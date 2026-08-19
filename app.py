"""
InvestIA PRO
Aplicação principal

Versão: v0.6
Fase: 2.9.6 - Estabilidade e Validação de Dados
"""

import streamlit as st


# ==========================================================
# IMPORTS
# ==========================================================

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
    Obtém um valor da análise aceitando
    nomes alternativos.
    """

    if not isinstance(
        result,
        dict,
    ):
        return default

    for key in keys:

        if key in result:

            value = result[key]

            if value is not None:

                return value

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


def safe_int(
    value,
    default=0,
):
    """
    Converte valores inteiros com segurança.
    """

    try:

        if value is None:
            return default

        return int(
            round(
                float(value)
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        return default


def safe_reasons(
    reasons,
):
    """
    Garante que justificativas possam
    ser exibidas sem quebrar a aplicação.
    """

    if reasons is None:

        return []

    if isinstance(
        reasons,
        list,
    ):

        return reasons

    return [reasons]


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
        f"Buscando dados de {asset}..."
    ):

        try:

            market_data = get_market_data(
                asset,
                period,
            )

        except Exception as error:

            st.error(
                f"Não foi possível obter dados "
                f"para {asset}."
            )

            st.caption(
                "O provedor de mercado pode estar "
                "temporariamente indisponível ou "
                "ter aplicado limite de requisições."
            )

            with st.expander(
                "Detalhes técnicos"
            ):

                st.exception(
                    error
                )

            st.stop()

    # ======================================================
    # VALIDAÇÃO DO RETORNO DO MARKET.PY
    # ======================================================

    if market_data is None:

        st.error(
            f"Não foi possível obter dados "
            f"para {asset}."
        )

        st.info(
            "Tente novamente em alguns instantes."
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
    # VALIDAÇÃO DO PREPARED_DATA
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
            "O formato dos dados preparados "
            "é inválido."
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

        st.caption(
            "O provedor não retornou uma série "
            "histórica válida."
        )

        st.stop()

    # ======================================================
    # VERIFICAÇÃO DO HISTÓRICO
    # ======================================================

    try:

        if history.empty:

            st.error(
                "O histórico do ativo está vazio."
            )

            st.stop()

    except AttributeError:

        st.error(
            "O histórico retornado possui "
            "formato inválido."
        )

        st.stop()

    # ======================================================
    # PREÇO ATUAL
    # ======================================================

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
                "Erro ao calcular os indicadores "
                "técnicos."
            )

            with st.expander(
                "Detalhes técnicos"
            ):

                st.exception(
                    error
                )

            st.stop()

    # ======================================================
    # VALIDAÇÃO DOS INDICADORES
    # ======================================================

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
    )

    # ======================================================
    # DADOS PARA ANÁLISE
    # ======================================================

    analysis_data = {

        "asset":
            asset,

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
    # VALIDAÇÃO
    # ======================================================

    try:

        data_validation = validate_analysis_data(
            analysis_data
        )

    except Exception:

        data_validation = True

    # ======================================================
    # COMPATIBILIDADE COM DIFERENTES
    # VERSÕES DO utils.py
    # ======================================================

    if isinstance(
        data_validation,
        dict,
    ):

        validation_valid = data_validation.get(
            "valid",
            False,
        )

        if not validation_valid:

            status = data_validation.get(
                "status",
                "INCOMPLETO",
            )

            message = data_validation.get(
                "message",
                "Dados insuficientes para análise.",
            )

            st.warning(
                f"⚠️ Dados insuficientes — {status}"
            )

            st.info(
                message
            )

            missing = data_validation.get(
                "missing",
                [],
            )

            invalid = data_validation.get(
                "invalid",
                [],
            )

            if missing:

                st.write(
                    "**Dados ausentes:** "
                    + ", ".join(
                        missing
                    )
                )

            if invalid:

                st.write(
                    "**Dados inválidos:** "
                    + ", ".join(
                        invalid
                    )
                )

            st.stop()

    elif data_validation is False:

        st.warning(
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
    # STATUS DA ANÁLISE
    # ======================================================

    analysis_valid = result.get(
        "valid",
        True,
    )

    analysis_status = result.get(
        "status",
        "CONSISTENTE",
    )

    analysis_message = result.get(
        "message",
        "",
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
        default="INDISPONÍVEL",
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
        default="Indisponível",
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
        default="Indisponível",
    )

    rsi_status = get_analysis_value(
        result,
        "rsi_status",
        default="Indisponível",
    )

    reasons = safe_reasons(
        get_analysis_value(
            result,
            "reasons",
            "justificativas",
            default=[],
        )
    )

    breakdown = get_analysis_value(
        result,
        "breakdown",
        default={},
    )

    if not isinstance(
        breakdown,
        dict,
    ):

        breakdown = {}

    executive_summary = get_analysis_value(
        result,
        "executive_summary",
        default="",
    )

    # ======================================================
    # CABEÇALHO DA ANÁLISE
    # ======================================================

    st.divider()

    st.header(
        f"📊 Análise do ativo: {asset}"
    )

    # ======================================================
    # STATUS
    # ======================================================

    if analysis_valid:

        st.success(
            f"🟢 Dados da análise: {analysis_status}"
        )

    else:

        st.warning(
            f"⚠️ Dados da análise: {analysis_status}"
        )

        if analysis_message:

            st.info(
                analysis_message
            )

    # ======================================================
    # CARDS PRINCIPAIS
    # ======================================================

    col1, col2, col3, col4 = st.columns(
        4
    )

    with col1:

        try:

            price_display = format_currency(
                price
            )

        except Exception:

            price_display = (
                f"R$ {safe_number(price):,.2f}"
            )

        st.metric(
            "Preço atual",
            price_display,
        )

    with col2:

        if score is None:

            score_display = "N/D"

        else:

            score_display = (
                f"{safe_int(score)}/100"
            )

        st.metric(
            "Score InvestIA",
            score_display,
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

        try:

            ma21_display = format_currency(
                ma21
            )

        except Exception:

            ma21_display = "N/D"

        st.metric(
            "MA21",
            ma21_display,
        )

    with ind2:

        try:

            ma200_display = format_currency(
                ma200
            )

        except Exception:

            ma200_display = "N/D"

        st.metric(
            "MA200",
            ma200_display,
        )

    with ind3:

        if rsi is None:

            rsi_display = "N/D"

        else:

            rsi_display = (
                f"{safe_number(rsi):.2f}"
            )

        st.metric(
            "RSI",
            rsi_display,
        )

    with ind4:

        if volatility is None:

            volatility_display = "N/D"

        else:

            volatility_percent = (
                safe_number(
                    volatility
                )
                * 100
            )

            volatility_display = (
                f"{volatility_percent:.2f}%"
            )

        st.metric(
            "Volatilidade",
            volatility_display,
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
    # BASE
    # ======================================================

    base_points = breakdown.get(
        "base",
        50,
    )

    base_points = safe_int(
        base_points,
        50,
    )

    st.write(
        f"**Base:** {base_points:+d} pontos"
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

        ma21_points = safe_int(
            ma21_data.get(
                "points",
                0,
            )
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
            str(
                ma21_reason
            )
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

        ma200_points = safe_int(
            ma200_data.get(
                "points",
                0,
            )
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
            str(
                ma200_reason
            )
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

        rsi_points = safe_int(
            rsi_data.get(
                "points",
                0,
            )
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
            str(
                rsi_reason
            )
        )

    # ======================================================
    # SCORE FINAL
    # ======================================================

    raw_score = breakdown.get(
        "raw_score"
    )

    if score is not None:

        score_final = safe_int(
            score
        )

        if raw_score is not None:

            raw_score_display = safe_number(
                raw_score
            )

            st.success(
                f"**Score final: {score_final}/100** "
                f"| Cálculo bruto: "
                f"{raw_score_display:.0f}"
            )

        else:

            st.success(
                f"**Score final: {score_final}/100**"
            )

    else:

        st.warning(
            "**Score final:** indisponível"
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

    # ======================================================
    # JUSTIFICATIVAS
    # ======================================================

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

            icon = "⚪"

        st.write(
            f"{icon} **{risk}**"
        )

        if score is not None:

            st.write(
                f"**Score:** "
                f"{safe_int(score)}/100"
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

    summary1, summary2 = st.columns(
        2
    )

    with summary1:

        st.write(
            f"**Ativo:** {asset}"
        )

        try:

            summary_price = format_currency(
                price
            )

        except Exception:

            summary_price = "N/D"

        st.write(
            f"**Preço:** "
            f"{summary_price}"
        )

        if score is not None:

            st.write(
                f"**Score:** "
                f"{safe_int(score)}/100"
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
            f"**Sinal:** "
            f"{qualified_signal}"
        )

        try:

            final_risk_icon = risk_icon(
                risk
            )

        except Exception:

            final_risk_icon = "⚪"

        st.write(
            f"**Risco:** "
            f"{final_risk_icon} {risk}"
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
   risco e recomendação.

### Exemplos

`PETR4` · `VALE3` · `ITUB4`

---

### 📌 Fase atual

**InvestIA PRO v0.6 — Fase 2.9.6**

Nesta versão o sistema possui:

- Validação dos dados de entrada
- Proteção contra dados ausentes
- Proteção contra valores inválidos
- Score InvestIA
- Explicabilidade do Score
- Análise de tendência
- Análise de RSI
- Classificação de risco
- Recomendação
- Resumo executivo
- Gráfico histórico
- Tratamento de erros
"""
    )
