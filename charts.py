"""
===========================================
InvestIA PRO
charts.py
Gráficos do Sistema
Versão 0.5.2
===========================================
"""

import plotly.graph_objects as go


# ==========================================
# Candlestick + Médias Móveis
# ==========================================

def grafico_medias(df, ticker):

    fig = go.Figure()

    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Preço"
        )
    )

    # Médias
    medias = [
        ("MM9", "MM9"),
        ("MM21", "MM21"),
        ("MM72", "MM72"),
        ("MM200", "MM200")
    ]

    for coluna, nome in medias:

        if coluna in df.columns:

            fig.add_trace(

                go.Scatter(

                    x=df.index,

                    y=df[coluna],

                    mode="lines",

                    name=nome

                )

            )

    fig.update_layout(

        title=f"{ticker}",

        height=600,

        template="plotly_white",

        xaxis_rangeslider_visible=False,

        legend=dict(

            orientation="h",

            yanchor="bottom",

            y=1.02,

            xanchor="left",

            x=0

        )

    )

    return fig


# ==========================================
# Volume
# ==========================================

def grafico_volume(df):

    fig = go.Figure()

    fig.add_trace(

        go.Bar(

            x=df.index,

            y=df["Volume"],

            name="Volume"

        )

    )

    fig.update_layout(

        title="Volume",

        height=250,

        template="plotly_white"

    )

    return fig


# ==========================================
# RSI
# ==========================================

def grafico_rsi(df):

    if "RSI" not in df.columns:

        return go.Figure()

    fig = go.Figure()

    fig.add_trace(

        go.Scatter(

            x=df.index,

            y=df["RSI"],

            mode="lines",

            name="RSI"

        )

    )

    fig.add_hline(y=70)

    fig.add_hline(y=30)

    fig.update_layout(

        title="RSI",

        height=250,

        template="plotly_white"

    )

    return fig


# ==========================================
# MACD
# ==========================================

def grafico_macd(df):

    if "MACD" not in df.columns:

        return go.Figure()

    fig = go.Figure()

    fig.add_trace(

        go.Scatter(

            x=df.index,

            y=df["MACD"],

            mode="lines",

            name="MACD"

        )

    )

    if "MACD_SINAL" in df.columns:

        fig.add_trace(

            go.Scatter(

                x=df.index,

                y=df["MACD_SINAL"],

                mode="lines",

                name="Sinal"

            )

        )

    fig.update_layout(

        title="MACD",

        height=250,

        template="plotly_white"

    )

    return fig
