"""
InvestIA PRO — Módulo de Gráficos Profissional
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots

PRO_THEME = {
    "bg_color": "#131722",
    "paper_bg": "#1e222d",
    "text_color": "#d1d4dc",
    "grid_color": "#2a2e3d",
    "bull_color": "#089981",
    "bear_color": "#f23645",
    "accent_blue": "#2962ff",
    "accent_gold": "#ffb74d"
}

def create_price_chart(analysis_res):
    """Gera gráfico financeiro avançado com Candlestick, MVs e RSI no estilo TradingView."""
    df = analysis_res["historical_data"]
    
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.75, 0.25],
        subplot_titles=(f"<b>Ação da Cotação — {analysis_res['asset']}</b>", "<b>Índice de Força Relativa (RSI 14)</b>")
    )

    # Candles
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name="Preço",
        increasing_line_color=PRO_THEME["bull_color"],
        decreasing_line_color=PRO_THEME["bear_color"]
    ), row=1, col=1)

    # Médias Móveis
    if 'MA21' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['MA21'], name="Média 21d", line=dict(color="#2962ff", width=1.5)), row=1, col=1)
    if 'MA200' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], name="Média 200d", line=dict(color="#ff9800", width=1.5)), row=1, col=1)

    # RSI
    if 'RSI' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI (14)", line=dict(color="#ab47bc", width=1.8)), row=2, col=1)
        # Linhas de sobrecompra/sobrevenda
        fig.add_hline(y=70, line_dash="dash", line_color="#f23645", line_width=1, row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#089981", line_width=1, row=2, col=1)

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor=PRO_THEME["bg_color"],
        paper_bgcolor=PRO_THEME["paper_bg"],
        font=dict(color=PRO_THEME["text_color"], family="Inter, sans-serif"),
        margin=dict(l=20, r=20, t=40, b=20),
        height=520,
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig.update_xaxes(gridcolor=PRO_THEME["grid_color"], showgrid=True)
    fig.update_yaxes(gridcolor=PRO_THEME["grid_color"], showgrid=True)

    return fig

def create_scanner_summary_chart(df_results):
    """Gera gráfico executivo de ranking de scores por ativo."""
    df_sorted = df_results.sort_values(by="Score", ascending=True)

    colors = []
    for s in df_sorted["Score"]:
        if s >= 70:
            colors.append(PRO_THEME["bull_color"])
        elif s <= 40:
            colors.append(PRO_THEME["bear_color"])
        else:
            colors.append(PRO_THEME["accent_gold"])

    fig = go.Figure(go.Bar(
        x=df_sorted["Score"],
        y=df_sorted["Ativo"],
        orientation='h',
        marker=dict(color=colors, cornerradius=4),
        text=df_sorted["Score"],
        textposition='outside'
    ))

    fig.update_layout(
        title="<b>Ranking InvestIA PRO — Comparativo de Score</b>",
        template="plotly_dark",
        plot_bgcolor=PRO_THEME["bg_color"],
        paper_bgcolor=PRO_THEME["paper_bg"],
        font=dict(color=PRO_THEME["text_color"], family="Inter, sans-serif"),
        height=max(350, len(df_results) * 35),
        margin=dict(l=20, r=40, t=50, b=20),
        xaxis=dict(range=[0, 105], gridcolor=PRO_THEME["grid_color"]),
        yaxis=dict(gridcolor=PRO_THEME["grid_color"])
    )

    return fig
