"""
InvestIA PRO
Aplicação principal

Versão: v0.6
Fase: 2.8.3 - Dashboard Executivo
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


def get_indicator_value(
    indicators,
    key,
    default=None,
):
    """
    Obtém um indicador com segurança.
    """

    if not isinstance(indicators, dict):
        return default

    value = indicators.get(key, default)

    return value


def get_analysis_value(
    result,
    *keys,
    default=None,
):
    """
    Obtém valores do resultado da análise
    aceitando nomes alternativos.
    """

    if not isinstance(result, dict):
        return default

    for key in keys:

        if key in result:

            value = result[key]

            if value is not None:
                return value

    return default


def normalize_market_data(
    market_data,
    asset,
):
    """
    Normaliza o retorno do market.py.

    Aceita:

    1. DataFrame diretamente
    2. Dicionário contendo:
       {
           "asset": ...,
           "price": ...,
           "history": DataFrame
       }

    Retorna sempre um dicionário padronizado.
    """

    # ------------------------------------------------------
    # DataFrame diretamente
    # ------------------------------------------------------

    if isinstance(
        market_data,
        pd.DataFrame,
    ):

        if market_data.empty:
            return None

        return {
            "asset": asset,
            "price": None,
            "history": market_data,
        }

    # ------------------------------------------------------
    # Dicionário
    # ------------------------------------------------------

    if isinstance(
        market_data,
        dict,
    ):

        normalized = dict(
            market_data
        )

        history = normalized.get(
            "history"
        )

        # ----------------------------------------------
        # Caso history exista
        # ----------------------------------------------

        if isinstance(
            history,
            pd.DataFrame,
        ):

            if history.empty:
                return None

            normalized["history"] = history

        # ----------------------------------------------
        # Caso o próprio dicionário contenha DataFrame
        # em outro campo
        # ----------------------------------------------

        elif history is None:

            for key in [
                "data",
                "df",
                "historical",
            ]:

                candidate = normalized.get(
                    key
                )

                if isinstance(
                    candidate,
                    pd.DataFrame,
                ):

                    if not candidate.empty:

                        normalized["history"] = (
                            candidate
                        )

                        break

        # ----------------------------------------------
        # Asset
        # ----------------------------------------------

        if not normalized.get("asset"):

            normalized["asset"] = asset

        return normalized

    return None


def normalize_prepared_data(
    prepared_data,
    asset,
):
    """
    Garante que o objeto preparado pelo market.py
    possua os campos mínimos esperados pelas demais
    camadas da aplicação.
    """

    if isinstance(
        prepared_data,
        pd.DataFrame,
    ):

        if prepared_data.empty:
            return None

        return {
            "asset": asset,
            "price": None,
            "history": prepared_data,
        }

    if not isinstance(
        prepared_data,
        dict,
    ):

        return None

    data = dict(
        prepared_data
    )

    # ------------------------------------------------------
    # Asset
    # ------------------------------------------------------

    if not data.get("asset"):

        data["asset"] = asset

    # ------------------------------------------------------
    # History
    # ------------------------------------------------------

    history = data.get(
        "history"
    )

    if not isinstance(
        history,
        pd.DataFrame,
    ):

        for key in [
            "data",
            "df",
            "historical",
        ]:

            candidate = data.get(
                key
            )

            if isinstance(
                candidate,
                pd.DataFrame,
            ):

                history = candidate

                data["history"] = (
                    candidate
                )

                break

    if not isinstance(
        history,
        pd.DataFrame,
    ):

        return None

    if history.empty:

        return None

    return data


def safe_numeric(
    value,
    default=None,
):
    """
    Converte valores numéricos com segurança.
    """

    try:

        if value is None:
            return default

        number = float(value)

        if pd.isna(number):
            return default

        return number

    except (
        TypeError,
        ValueError,
    ):

        return default


def safe_text(
    value,
    default="N/A",
):
    """
    Converte qualquer valor para texto.
    """

    if value is None:
        return default

    text = str(value).strip()

    if not text:
        return default

    return text


def get_history_from_data(
    data,
):
    """
    Recupera o histórico de forma segura.
    """

    if not isinstance(
        data,
        dict,
    ):

        return None

    history = data.get(
        "history"
    )

    if isinstance(
        history,
        pd.DataFrame,
    ):

        return history

    return None


def build_analysis_data(
    price,
    indicators,
):
    """
    Monta o objeto utilizado pelo analysis.py.
    """

    return {

        "price":
            price,

        "rsi":
            get_indicator_value(
                indicators,
                "rsi",
            ),

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

        "volatility":
            get_indicator_value(
                indicators,
                "volatility",
            ),
    }


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

col_input, col_period = st.columns(
    [3, 1]
)


with col_input:

    asset_input = st.text_input(
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
    # BUSCA DE MERCADO
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
                "Não foi possível obter os dados "
                f"para {asset}."
            )

            with st.expander(
                "Detalhes técnicos"
            ):

                st.exception(
                    error
                )

            st.stop()

    # ======================================================
    # NORMALIZAÇÃO DO RETORNO
    # ======================================================

    market_data = normalize_market_data(
        market_data,
        asset,
    )

    if market_data is None:

        st.error(
            f"Não foi possível obter dados "
            f"para {asset}."
        )

        st.info(
            "Verifique o código do ativo e tente novamente."
        )

        st.stop()

    # ======================================================
    # PREPARAÇÃO
    # ======================================================

    with st.spinner(
        "Preparando dados..."
    ):

        try:

            prepared_data = prepare_market_data(
                market_data
            )

        except Exception as error:

            st.error(
                "Erro ao preparar os dados do mercado."
            )

            with st.expander(
                "Detalhes técnicos"
            ):

                st.exception(
                    error
                )

            st.stop()

    # ======================================================
    # NORMALIZAÇÃO FINAL
    # ======================================================

    prepared_data = normalize_prepared_data(
        prepared_data,
        asset,
    )

    if prepared_data is None:

        st.error(
            "Os dados do mercado não puderam "
            "ser preparados corretamente."
        )

        st.stop()

    # ======================================================
    # GARANTIR AS CHAVES PRINCIPAIS
    # ======================================================

    prepared_data.setdefault(
        "asset",
        asset,
    )

    history = get_history_from_data(
        prepared_data
    )

    if history is None:

        st.error(
            "O histórico do ativo não foi encontrado."
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

    price = safe_numeric(
        price
    )

    # ------------------------------------------------------
    # Fallback para o último fechamento
    # ------------------------------------------------------

    if price is None:

        try:

            if "Close" in history.columns:

                price = safe_numeric(
                    history["Close"]
                    .dropna()
                    .iloc[-1]
                )

            elif "close" in history.columns:

                price = safe_numeric(
                    history["close"]
                    .dropna()
                    .iloc[-1]
                )

        except Exception:

            price = None

    if price is None:

        st.error(
            "Não foi possível determinar "
            "o preço atual."
        )

        st.stop()

    # Garantir preço no objeto
    prepared_data["price"] = price
    prepared_data["asset"] = asset

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

            with st.expander(
                "Detalhes técnicos"
            ):

                st.exception(
                    error
                )

            st.stop()

    if not isinstance(
        indicators,
        dict,
    ):

        st.error(
            "Os indicadores não foram retornados "
            "em formato válido."
        )

        st.stop()

    # ======================================================
    # DADOS PARA ANÁLISE
    # ======================================================

    analysis_data = build_analysis_data(
        price,
        indicators,
    )

    # ======================================================
    # VALIDAÇÃO DOS INDICADORES
    # ======================================================

    if not validate_analysis_data(
        analysis_data
    ):

        st.warning(
            "Os dados disponíveis não são suficientes "
            "para realizar uma análise confiável."
        )

        # Diagnóstico
        st.subheader(
            "🔎 Diagnóstico dos dados"
        )

        diag1, diag2 = st.columns(
            2
        )

        with diag1:

            st.markdown(
                "### Mercado"
            )

            st.success(
                f"✓ {asset}"
            )

            st.write(
                f"Preço: {format_currency(price)}"
            )

        with diag2:

            st.markdown(
                "### Indicadores"
            )

            for field in [
                "rsi",
                "ma21",
                "ma200",
                "volatility",
            ]:

                value = analysis_data.get(
                    field
                )

                if value is None:

                    st.error(
                        f"✗ {field.upper()} indisponível"
                    )

                else:

                    st.success(
                        f"✓ {field.upper()}"
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

    if not isinstance(
        result,
        dict,
    ):

        st.error(
            "A análise não retornou um resultado válido."
        )

        st.stop()

    # ======================================================
    # EXTRAÇÃO DOS RESULTADOS
    # ======================================================

    score = safe_numeric(
        get_analysis_value(
            result,
            "score",
            default=0,
        ),
        0,
    )

    classification = safe_text(
        get_analysis_value(
            result,
            "classification",
            default="NEUTRO",
        ),
        "NEUTRO",
    )

    signal = safe_text(
        get_analysis_value(
            result,
            "signal",
            default="NEUTRO",
        ),
        "NEUTRO",
    )

    qualified_signal = safe_text(
        get_analysis_value(
            result,
            "qualified_signal",
            default=signal,
        ),
        signal,
    )

    signal_level = safe_text(
        get_analysis_value(
            result,
            "signal_level",
            default="Aguardar",
        ),
        "Aguardar",
    )

    signal_icon = safe_text(
        get_analysis_value(
            result,
            "signal_icon",
            default="🟡",
        ),
        "🟡",
    )

    trend = safe_text(
        get_analysis_value(
            result,
            "trend",
            "tendencia",
            default="Neutra",
        ),
        "Neutra",
    )

    recommendation = safe_text(
        get_analysis_value(
            result,
            "recommendation",
            "recomendacao",
            default="Aguardar",
        ),
        "Aguardar",
    )

    risk = safe_text(
        get_analysis_value(
            result,
            "risk",
            "risco",
            default="Moderado",
        ),
        "Moderado",
    )

    rsi_status = safe_text(
        get_analysis_value(
            result,
            "rsi_status",
            default="Neutro",
        ),
        "Neutro",
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

        reasons = [
            str(reasons)
        ]

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

    executive_summary = safe_text(
        get_analysis_value(
            result,
            "executive_summary",
            default="",
        ),
        "",
    )

    # ======================================================
    # DASHBOARD EXECUTIVO
    # ======================================================

    st.divider()

    st.header(
        f"📊 Dashboard Executivo — {asset}"
    )

    st.caption(
        f"Período analisado: {period}"
    )

    # ======================================================
    # VISÃO GERAL
    # ======================================================

    st.subheader(
        "🎯 Visão Geral"
    )

    overview1, overview2, overview3, overview4 = (
        st.columns(4)
    )

    with overview1:

        st.metric(
            "Preço",
            format_currency(
                price
            ),
        )

    with overview2:

        st.metric(
            "Score InvestIA",
            f"{int(round(score))}/100",
        )

    with overview3:

        st.metric(
            "Tendência",
            trend,
        )

    with overview4:

        st.metric(
            "Risco",
            f"{risk_icon(risk)} {risk}",
        )

    # ======================================================
    # SINAL INVESTIA
    # ======================================================

    st.divider()

    st.subheader(
        "🎯 Sinal InvestIA"
    )

    signal_col1, signal_col2 = st.columns(
        [2, 1]
    )

    with signal_col1:

        if "COMPRA" in qualified_signal.upper():

            st.success(
                f"🟢 **{qualified_signal}**"
            )

        elif "VENDA" in qualified_signal.upper():

            st.error(
                f"🔴 **{qualified_signal}**"
            )

        else:

            st.warning(
                f"🟡 **{qualified_signal}**"
            )

        st.caption(
            "Combinação técnica baseada nos indicadores disponíveis."
        )

    with signal_col2:

        st.metric(
            "Nível do sinal",
            f"{signal_icon} {signal_level}",
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
    # GESTÃO DE RISCO
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
            "Score de segurança",
            f"{max(0, 100 - abs(50 - score) * 2):.0f}/100",
        )

    with risk_col3:

        rsi_value = safe_numeric(
            analysis_data.get("rsi")
        )

        if rsi_value is not None:

            st.metric(
                "RSI",
                f"{rsi_value:.2f}",
            )

        else:

            st.metric(
                "RSI",
                "N/A",
            )

    st.info(
        f"**Risco {risk.lower()}.** "
        "Utilize os indicadores em conjunto e considere "
        "o contexto operacional antes de tomar uma decisão."
    )

    # ======================================================
    # ALERTAS TÉCNICOS
    # ======================================================

    st.divider()

    st.subheader(
        "⚠️ Alertas Técnicos"
    )

    alerts = []

    rsi_value = safe_numeric(
        analysis_data.get("rsi")
    )

    ma21_value = safe_numeric(
        analysis_data.get("ma21")
    )

    ma200_value = safe_numeric(
        analysis_data.get("ma200")
    )

    volatility_value = safe_numeric(
        analysis_data.get("volatility")
    )

    if rsi_value is not None:

        if rsi_value >= 70:

            alerts.append(
                "RSI em região de sobrecompra."
            )

        elif rsi_value <= 30:

            alerts.append(
                "RSI em região de sobrevenda."
            )

    if (
        price is not None
        and ma21_value is not None
    ):

        if price > ma21_value:

            alerts.append(
                "Preço acima da MA21."
            )

        elif price < ma21_value:

            alerts.append(
                "Preço abaixo da MA21."
            )

    if (
        price is not None
        and ma200_value is not None
    ):

        if price > ma200_value:

            alerts.append(
                "Preço acima da MA200."
            )

        elif price < ma200_value:

            alerts.append(
                "Preço abaixo da MA200."
            )

    if volatility_value is not None:

        volatility_percent = (
            volatility_value * 100
        )

        if volatility_percent >= 3:

            alerts.append(
                "Volatilidade diária elevada."
            )

    if alerts:

        for alert in alerts:

            st.warning(
                f"⚠️ {alert}"
            )

    else:

        st.success(
            "✅ Nenhum alerta técnico relevante identificado."
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
                ma21_value
            ),
        )

    with ind2:

        st.metric(
            "MA200",
            format_currency(
                ma200_value
            ),
        )

    with ind3:

        if rsi_value is not None:

            st.metric(
                "RSI",
                f"{rsi_value:.2f}",
            )

        else:

            st.metric(
                "RSI",
                "N/A",
            )

    with ind4:

        if volatility_value is not None:

            st.metric(
                "Volatilidade",
                f"{volatility_value * 100:.2f}%",
            )

        else:

            st.metric(
                "Volatilidade",
                "N/A",
            )

    # ======================================================
    # GRÁFICO
    # ======================================================

    st.divider()

    st.subheader(
        "📊 Evolução do Preço"
    )

    try:

        # --------------------------------------------------
        # Fase 2.8.3
        #
        # O charts.py atual recebe:
        #
        # create_price_chart(
        #     history,
        #     indicators
        # )
        # --------------------------------------------------

        try:

            fig = create_price_chart(
                history,
                indicators,
            )

        except TypeError:

            # Compatibilidade com versões anteriores
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
                "O gráfico não pôde ser gerado."
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
    # COMPOSIÇÃO DO SCORE
    # ======================================================

    st.divider()

    st.subheader(
        "🧠 Composição do Score InvestIA"
    )

    st.caption(
        "O Score é composto pela combinação dos indicadores técnicos."
    )

    base_points = breakdown.get(
        "base",
        50,
    )

    raw_score = breakdown.get(
        "raw_score"
    )

    bd1, bd2, bd3 = st.columns(
        3
    )

    # ------------------------------------------------------
    # MA21
    # ------------------------------------------------------

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

        ma21_points = safe_numeric(
            ma21_data.get(
                "points",
                0,
            ),
            0,
        )

        ma21_signal = safe_text(
            ma21_data.get(
                "signal",
                "Neutro",
            ),
            "Neutro",
        )

        ma21_reason = safe_text(
            ma21_data.get(
                "reason",
                "Sem informação.",
            ),
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

        ma200_data = breakdown.get(
            "ma200",
            {},
        )

        if not isinstance(
            ma200_data,
            dict,
        ):

            ma200_data = {}

        ma200_points = safe_numeric(
            ma200_data.get(
                "points",
                0,
            ),
            0,
        )

        ma200_signal = safe_text(
            ma200_data.get(
                "signal",
                "Neutro",
            ),
            "Neutro",
        )

        ma200_reason = safe_text(
            ma200_data.get(
                "reason",
                "Sem informação.",
            ),
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

        rsi_data = breakdown.get(
            "rsi",
            {},
        )

        if not isinstance(
            rsi_data,
            dict,
        ):

            rsi_data = {}

        rsi_points = safe_numeric(
            rsi_data.get(
                "points",
                0,
            ),
            0,
        )

        rsi_signal = safe_text(
            rsi_data.get(
                "signal",
                "Neutro",
            ),
            "Neutro",
        )

        rsi_reason = safe_text(
            rsi_data.get(
                "reason",
                "Sem informação.",
            ),
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

    st.divider()

    if raw_score is not None:

        raw_score_value = safe_numeric(
            raw_score,
            score,
        )

        st.success(
            f"**Score final: {int(round(score))}/100** "
            f"| Base: {base_points} | "
            f"Score bruto: {raw_score_value:.0f}"
        )

    else:

        st.success(
            f"**Score final: {int(round(score))}/100**"
        )

    # ======================================================
    # ANÁLISE DETALHADA
    # ======================================================

    st.divider()

    st.subheader(
        "🔎 Análise Detalhada"
    )

    detail_col1, detail_col2 = st.columns(
        2
    )

    # ------------------------------------------------------
    # FUNDAMENTAÇÃO
    # ------------------------------------------------------

    with detail_col1:

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
                "Nenhuma justificativa foi retornada."
            )

    # ------------------------------------------------------
    # GESTÃO DE RISCO
    # ------------------------------------------------------

    with detail_col2:

        st.markdown(
            "### 🛡️ Gestão de risco"
        )

        st.write(
            f"{risk_icon(risk)} **{risk}**"
        )

        st.write(
            f"**Score:** {int(round(score))}/100"
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
            f"**Preço:** {format_currency(price)}"
        )

        st.write(
            f"**Score:** {int(round(score))}/100"
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
            f"**Risco:** {risk_icon(risk)} {risk}"
        )

        st.write(
            f"**Recomendação:** {recommendation}"
        )

else:

    # ======================================================
    # TELA INICIAL
    # ======================================================

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
4. Consulte o Dashboard Executivo.

### Exemplos

`PETR4` · `VALE3` · `ITUB4`
"""
    )
