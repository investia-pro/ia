"""
InvestIA PRO
Gráficos

Versão: v0.5.3 Stable
"""

import plotly.graph_objects as go

from config import (
    SHORT_MA,
    LONG_MA,
    THEME
)


def create_price_chart(history, indicators):
    """
    Cria gráfico principal do ativo.

    Parameters
    ----------
    history : pandas.DataFrame

    indicators : dict

    Returns
    -------
    plotly.graph_objects.Figure
    """

    df = history.copy()

    # ===============================
    # Médias móveis
    # ===============================

    df["MA21"] = (
        df["Close"]
        .rolling(SHORT_MA)
        .mean()
    )

    df["MA200"] = (
        df["Close"]
        .rolling(LONG_MA)
        .mean()
    )

    # ===============================
    # Figura
    # ===============================

    fig = go.Figure()

    # -------------------------------
    # Preço
    # -------------------------------

    fig.add_trace(

        go.Scatter(

            x=df.index,

            y=df["Close"],

            mode="lines",

            name="Preço",

            line=dict(
                width=2
            )

        )

    )

    # -------------------------------
    # MA21
    # -------------------------------

    fig.add_trace(

        go.Scatter(

            x=df.index,

            y=df["MA21"],

            mode="lines",

            name=f"MA {SHORT_MA}",

            line=dict(
                dash="dot"
            )

        )

    )

    # -------------------------------
    # MA200
    # -------------------------------

    fig.add_trace(

        go.Scatter(

            x=df.index,

            y=df["MA200"],

            mode="lines",

            name=f"MA {LONG_MA}",

            line=dict(
                dash="dash"
            )

        )

    )

    # ===============================
    # Layout
    # ===============================

    fig.update_layout(

        template=THEME,

        height=600,

        hovermode="x unified",

        legend=dict(
            orientation="h",
            y=1.05
        ),

        margin=dict(
            l=20,
            r=20,
            t=40,
            b=20
        ),

        xaxis_title="",

        yaxis_title="Preço"

    )

    return fig
