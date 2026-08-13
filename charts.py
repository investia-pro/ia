"""
InvestIA PRO
Gráficos

Versão: v0.6
Fase: 2.7.3 - Alertas Visuais e Indicadores
"""

import pandas as pd
import plotly.graph_objects as go


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def _find_column(df, candidates):
    """
    Localiza uma coluna existente no DataFrame.

    Aceita diferentes padrões de nomenclatura.
    """

    if df is None:
        return None

    for column in candidates:

        if column in df.columns:
            return column

    return None


def _prepare_history(history):
    """
    Prepara o histórico para construção do gráfico.
    """

    if history is None:
        return None

    if not isinstance(history, pd.DataFrame):
        return None

    if history.empty:
        return None

    data = history.copy()

    # ------------------------------------------------------
    # Índice
    # ------------------------------------------------------

    try:

        data.index = pd.to_datetime(
            data.index
        )

    except Exception:
        pass

    # ------------------------------------------------------
    # Ordenação
    # ------------------------------------------------------

    try:

        data = data.sort_index()

    except Exception:
        pass

    return data


def _calculate_moving_average(
    history,
    window,
):
    """
    Calcula uma média móvel diretamente do histórico.
    """

    close_column = _find_column(
        history,
        [
            "Close",
            "close",
            "Adj Close",
            "adj_close",
        ],
    )

    if close_column is None:
        return None

    try:

        return history[
            close_column
        ].rolling(
            window=window
        ).mean()

    except Exception:

        return None


def _add_price_trace(
    fig,
    history,
):
    """
    Adiciona a série de preço.
    """

    close_column = _find_column(
        history,
        [
            "Close",
            "close",
            "Adj Close",
            "adj_close",
        ],
    )

    if close_column is None:
        return False

    fig.add_trace(
        go.Scatter(
            x=history.index,
            y=history[close_column],
            mode="lines",
            name="Preço",
            line=dict(
                width=2,
            ),
            hovertemplate=(
                "Data: %{x|%d/%m/%Y}"
                "<br>Preço: R$ %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )

    return True


def _add_ma21_trace(
    fig,
    history,
):
    """
    Adiciona a média móvel de 21 períodos.
    """

    ma21 = _calculate_moving_average(
        history,
        21,
    )

    if ma21 is None:
        return False

    fig.add_trace(
        go.Scatter(
            x=history.index,
            y=ma21,
            mode="lines",
            name="MA21",
            line=dict(
                dash="dot",
                width=1.5,
            ),
            hovertemplate=(
                "Data: %{x|%d/%m/%Y}"
                "<br>MA21: R$ %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )

    return True


def _add_ma200_trace(
    fig,
    history,
):
    """
    Adiciona a média móvel de 200 períodos.
    """

    ma200 = _calculate_moving_average(
        history,
        200,
    )

    if ma200 is None:
        return False

    fig.add_trace(
        go.Scatter(
            x=history.index,
            y=ma200,
            mode="lines",
            name="MA200",
            line=dict(
                dash="dash",
                width=1.5,
            ),
            hovertemplate=(
                "Data: %{x|%d/%m/%Y}"
                "<br>MA200: R$ %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )

    return True


def _add_current_price_line(
    fig,
    history,
):
    """
    Adiciona uma referência horizontal
    para o último preço.
    """

    close_column = _find_column(
        history,
        [
            "Close",
            "close",
            "Adj Close",
            "adj_close",
        ],
    )

    if close_column is None:
        return

    try:

        current_price = float(
            history[
                close_column
            ].dropna().iloc[-1]
        )

    except Exception:

        return

    fig.add_hline(
        y=current_price,
        line_dash="dot",
        annotation_text=(
            f"Preço atual: R$ {current_price:.2f}"
        ),
        annotation_position="top right",
    )


def _add_crossing_alert(
    fig,
    history,
):
    """
    Identifica visualmente quando o preço
    cruza a MA21.

    A função utiliza o último ponto disponível.
    """

    close_column = _find_column(
        history,
        [
            "Close",
            "close",
            "Adj Close",
            "adj_close",
        ],
    )

    if close_column is None:
        return

    ma21 = _calculate_moving_average(
        history,
        21,
    )

    if ma21 is None:
        return

    try:

        valid = pd.DataFrame(
            {
                "price": history[
                    close_column
                ],
                "ma21": ma21,
            }
        ).dropna()

        if len(valid) < 2:
            return

        previous = valid.iloc[-2]
        current = valid.iloc[-1]

        crossed_up = (
            previous["price"]
            <= previous["ma21"]
            and
            current["price"]
            > current["ma21"]
        )

        crossed_down = (
            previous["price"]
            >= previous["ma21"]
            and
            current["price"]
            < current["ma21"]
        )

        if crossed_up:

            fig.add_annotation(
                x=valid.index[-1],
                y=current["price"],
                text="⬆ Cruzamento MA21",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-40,
            )

        elif crossed_down:

            fig.add_annotation(
                x=valid.index[-1],
                y=current["price"],
                text="⬇ Cruzamento MA21",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=40,
            )

    except Exception:

        return


def _add_trend_annotation(
    fig,
    history,
):
    """
    Adiciona uma indicação simples da tendência
    com base no preço versus MA21 e MA200.
    """

    close_column = _find_column(
        history,
        [
            "Close",
            "close",
            "Adj Close",
            "adj_close",
        ],
    )

    if close_column is None:
        return

    ma21 = _calculate_moving_average(
        history,
        21,
    )

    ma200 = _calculate_moving_average(
        history,
        200,
    )

    if ma21 is None or ma200 is None:
        return

    try:

        data = pd.DataFrame(
            {
                "price": history[
                    close_column
                ],
                "ma21": ma21,
                "ma200": ma200,
            }
        ).dropna()

        if data.empty:
            return

        last = data.iloc[-1]

        price = float(
            last["price"]
        )

        ma21_value = float(
            last["ma21"]
        )

        ma200_value = float(
            last["ma200"]
        )

        if (
            price > ma21_value
            and
            price > ma200_value
        ):

            trend = "Tendência: POSITIVA"

        elif (
            price < ma21_value
            and
            price < ma200_value
        ):

            trend = "Tendência: NEGATIVA"

        else:

            trend = "Tendência: MODERADA"

        fig.add_annotation(
            x=1,
            y=1,
            xref="paper",
            yref="paper",
            text=trend,
            showarrow=False,
            xanchor="right",
            yanchor="top",
        )

    except Exception:

        return


# ==========================================================
# GRÁFICO PRINCIPAL
# ==========================================================

def create_price_chart(
    history,
    indicators=None,
):
    """
    Cria o gráfico principal do ativo.

    Parâmetros
    ----------
    history : pandas.DataFrame
        Histórico de preços.

    indicators : dict, opcional
        Indicadores técnicos.

    Retorno
    -------
    plotly.graph_objects.Figure
    """

    history = _prepare_history(
        history
    )

    if history is None:
        return None


    # ======================================================
    # FIGURA
    # ======================================================

    fig = go.Figure()


    # ======================================================
    # PREÇO
    # ======================================================

    price_added = _add_price_trace(
        fig,
        history,
    )

    if not price_added:
        return None


    # ======================================================
    # MA21
    # ======================================================

    _add_ma21_trace(
        fig,
        history,
    )


    # ======================================================
    # MA200
    # ======================================================

    _add_ma200_trace(
        fig,
        history,
    )


    # ======================================================
    # PREÇO ATUAL
    # ======================================================

    _add_current_price_line(
        fig,
        history,
    )


    # ======================================================
    # ALERTA DE CRUZAMENTO
    # ======================================================

    _add_crossing_alert(
        fig,
        history,
    )


    # ======================================================
    # TENDÊNCIA
    # ======================================================

    _add_trend_annotation(
        fig,
        history,
    )


    # ======================================================
    # LAYOUT
    # ======================================================

    fig.update_layout(
        title="Evolução do preço e médias móveis",
        xaxis_title="Data",
        yaxis_title="Preço (R$)",
        hovermode="x unified",
        height=550,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        margin=dict(
            l=20,
            r=20,
            t=80,
            b=20,
        ),
    )


    # ======================================================
    # EIXO X
    # ======================================================

    fig.update_xaxes(
        rangeslider_visible=False,
    )


    # ======================================================
    # EIXO Y
    # ======================================================

    fig.update_yaxes(
        fixedrange=False,
    )


    return fig


# ==========================================================
# GRÁFICO SIMPLIFICADO
# ==========================================================

def create_simple_price_chart(
    history,
):
    """
    Cria uma versão simplificada do gráfico.
    """

    history = _prepare_history(
        history
    )

    if history is None:
        return None

    close_column = _find_column(
        history,
        [
            "Close",
            "close",
            "Adj Close",
            "adj_close",
        ],
    )

    if close_column is None:
        return None

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=history.index,
            y=history[close_column],
            mode="lines",
            name="Preço",
            line=dict(
                width=2,
            ),
            hovertemplate=(
                "Data: %{x|%d/%m/%Y}"
                "<br>Preço: R$ %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title="Evolução do preço",
        xaxis_title="Data",
        yaxis_title="Preço (R$)",
        hovermode="x unified",
        height=500,
    )

    return fig
