import plotly.graph_objects as go


# ==========================================
# Candlestick
# ==========================================

def grafico_candlestick(df, ticker):

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name=ticker
        )
    )

    fig.update_layout(

        title=ticker,

        height=500,

        xaxis_rangeslider_visible=False,

        margin=dict(
            l=5,
            r=5,
            t=40,
            b=5
        )
    )

    return fig


# ==========================================
# Candlestick + Médias Móveis
# ==========================================

def grafico_medias(df, ticker):

    fig = go.Figure()

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

    fig.add_trace(

        go.Scatter(

            x=df.index,

            y=df["Close"].rolling(9).mean(),

            mode="lines",

            name="MM9"

        )

    )

    fig.add_trace(

        go.Scatter(

            x=df.index,

            y=df["Close"].rolling(21).mean(),

            mode="lines",

            name="MM21"

        )

    )

    fig.add_trace(

        go.Scatter(

            x=df.index,

            y=df["Close"].rolling(72).mean(),

            mode="lines",

            name="MM72"

        )

    )

    fig.add_trace(

        go.Scatter(

            x=df.index,

            y=df["Close"].rolling(200).mean(),

            mode="lines",

            name="MM200"

        )

    )

    fig.update_layout(

        title=f"{ticker} - Médias Móveis",

        height=550,

        xaxis_rangeslider_visible=False

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

        height=250

    )

    return fig


# ==========================================
# RSI
# ==========================================

def grafico_rsi(df, rsi):

    fig = go.Figure()

    fig.add_trace(

        go.Scatter(

            x=df.index,

            y=rsi,

            mode="lines",

            name="RSI"

        )

    )

    fig.add_hline(y=70)

    fig.add_hline(y=30)

    fig.update_layout(

        title="RSI",

        height=250

    )

    return fig
