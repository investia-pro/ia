"""
InvestIA PRO — Aplicação Principal Streamlit
"""
import streamlit as st
import pandas as pd
import time
import sys
from pathlib import Path

# Configuração da página (DEVE ser a PRIMEIRA instrução Streamlit)
st.set_page_config(
    page_title="InvestIA PRO",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ajuste de path para importação no Streamlit Cloud
current_dir = Path(__file__).parent.resolve()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Importações dos módulos do projeto
from config import APP_TITLE, PAGE_ICON
from market import fetch_asset_data
from analysis import analyze_asset
from charts import create_price_chart, create_scanner_summary_chart
from utils import format_currency, format_percent

# Carregar CSS externo
def load_css():
    css_path = current_dir / "style.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Forçar tema escuro na sidebar para eliminar a barra branca lateral
st.markdown("""
<style>
    section[data-testid="stSidebar"] {
        background-color: #161922 !important;
        border-right: 1px solid #2a2e3d !important;
    }
    section[data-testid="stSidebar"] * {
        color: #e0e6ed !important;
    }
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117 !important;
        color: #e0e6ed !important;
    }
</style>
""", unsafe_allow_html=True)

# Listas Pré-configuradas para o Scanner
PRESET_LISTS = {
    "🔥 Principais Ações B3 (Top 30 Liquidez)": [
        "PETR4", "VALE3", "ITUB4", "BBAS3", "BBDC4", "ABEV3", "WEGE3", "PRIO3", "RENT3", "SUZB3",
        "B3SA3", "EQTL3", "ELET3", "RADL3", "RDOR3", "VBBR3", "VAMO3", "GGBR4", "CSAN3", "RAIZ4",
        "HAPV3", "CPLE6", "CMIG4", "UGPA3", "SANB11", "KLBN11", "EMBR3", "ALOS3", "MULT3", "TOTS3"
    ],
    "🏢 Fundos Imobiliários (FIIs)": [
        "HGLG11", "KNCR11", "MXRF11", "XPML11", "BTLG11", "VISC11", "TGAR11", "KNRI11", "CPTS11", "IRDM11"
    ],
    "🇺🇸 BDRs / Big Techs EUA": [
        "AAPL34", "MSFT34", "GOGL34", "AMZO34", "NVDC34", "TSLA34", "MELI34"
    ]
}

# Cabeçalho Principal
st.markdown("""
<div style="background: linear-gradient(90deg, #1e222d 0%, #141722 100%); padding: 24px; border-radius: 12px; border: 1px solid #2a2e3d; margin-bottom: 24px;">
    <h1 style="margin: 0; font-size: 2rem; color: #ffffff;">📈 InvestIA PRO</h1>
    <p style="margin: 4px 0 0 0; color: #848e9c; font-size: 0.95rem;">Plataforma de Inteligência Quantitativa e Terminal de Análise Financeira</p>
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("Navegação", ["Dashboard Executivo", "Scanner de Mercado", "Sobre o Projeto"])

if menu == "Dashboard Executivo":
    st.subheader("🔍 Análise Individual de Ativo")
    
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        ticker_input = st.text_input("Digite o Ticker do Ativo (ex: PETR4, VALE3, ITUB4):", value="PETR4")
    with col_btn:
        st.write("")
        st.write("")
        btn_analyze = st.button("ANALISAR", type="primary", use_container_width=True)

    if btn_analyze or ticker_input:
        with st.spinner(f"Coletando dados e analisando {ticker_input}..."):
            try:
                # Chamada segura conforme o módulo de mercado
                df_data, info_data = fetch_asset_data(ticker_input)
                
                if df_data is None or df_data.empty:
                    st.error(f"Erro: Não foi possível obter dados para o ticker '{ticker_input}'.")
                else:
                    res = analyze_asset(df_data, info_data)
                    res["historical_data"] = df_data
                    
                    # Cards Financeiros
                    c1, c2, c3, c4, c5 = st.columns(5)
                    c1.metric("Preço Atual", format_currency(res.get("price", 0)), delta=format_percent(res.get("change_percent", 0)))
                    c2.metric("Score InvestIA", f"{res.get('score', 0)} / 100", delta=res.get("signal", ""))
                    c3.metric("Classificação", res.get("classification", "-"))
                    c4.metric("Tendência", res.get("trend", "-"))
                    c5.metric("Nível de Risco", res.get("risk", "-"))

                    st.markdown("<br>", unsafe_allow_html=True)

                    col_left, col_right = st.columns([1, 1])

                    with col_left:
                        st.markdown("""
                        <div style="background: #1e222d; padding: 20px; border-radius: 10px; border: 1px solid #2a2e3d; height: 100%;">
                            <h3 style="margin-top:0;">📋 Resumo Executivo</h3>
                        """, unsafe_allow_html=True)
                        st.info(res.get("executive_summary", "Análise realizada com sucesso."))
                        st.markdown(f"**Recomendação:** `{res.get('recommendation', 'N/A')}`")

                        st.markdown("#### Justificativas do Sinal:")
                        for r in res.get("reasons", []):
                            st.write(f"• {r}")
                        st.markdown("</div>", unsafe_allow_html=True)

                    with col_right:
                        st.markdown("""
                        <div style="background: #1e222d; padding: 20px; border-radius: 10px; border: 1px solid #2a2e3d; height: 100%;">
                            <h3 style="margin-top:0;">📊 Decomposição do Score</h3>
                        """, unsafe_allow_html=True)
                        b = res.get("breakdown", {})
                        st.write(f"• **Tendência:** {b.get('trend_score', 0)} / 40 pts")
                        st.write(f"• **RSI:** {b.get('rsi_score', 0)} / 35 pts")
                        st.write(f"• **Volatilidade/Risco:** {b.get('volatility_score', 0)} / 25 pts")
                        
                        st.markdown("#### Detalhes Técnicos:")
                        st.write(f"• **RSI (14):** {res.get('rsi', 0)} ({res.get('rsi_status', '-')})")
                        st.write(f"• **MA 21:** {format_currency(res.get('ma21', 0))}")
                        st.write(f"• **MA 200:** {format_currency(res.get('ma200', 0))}")
                        st.write(f"• **Volatilidade Anual:** {res.get('volatility', 0):.2f}%")
                        st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    if res.get("historical_data") is not None:
                        st.plotly_chart(create_price_chart(res), use_container_width=True)
            except Exception as e:
                st.error(f"Ocorreu um erro durante o processamento: {str(e)}")

elif menu == "Scanner de Mercado":
    st.subheader("🎯 Scanner de Oportunidades Automático")
    st.caption("Varra o mercado em busca dos ativos com melhor Score InvestIA em tempo real.")

    col_sel1, col_sel2 = st.columns([2, 1])
    with col_sel1:
        preset_choice = st.selectbox("Selecione o Grupo de Ativos para Varredura:", list(PRESET_LISTS.keys()))
        selected_preset = PRESET_LISTS[preset_choice]
    
    with col_sel2:
        top_n = st.slider("Exibir Top N Melhores:", min_value=5, max_value=len(selected_preset), value=10)

    with st.expander("🛠️ Personalizar Lista de Ativos do Scan"):
        assets_to_scan = st.multiselect("Ativos incluídos na varredura:", options=selected_preset, default=selected_preset)

    if st.button("🚀 INICIAR VARREDURA DO MERCADO", type="primary"):
        results_list = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, symbol in enumerate(assets_to_scan):
            status_text.text(f"Analisando {symbol} ({i+1}/{len(assets_to_scan)})...")
            try:
                df_mkt, info_mkt = fetch_asset_data(symbol)
                if df_mkt is not None and not df_mkt.empty:
                    analysis = analyze_asset(df_mkt, info_mkt)
                    results_list.append({
                        "Ativo": analysis.get("asset", symbol),
                        "Preço (R$)": analysis.get("price", 0),
                        "Var. (%)": analysis.get("change_percent", 0),
                        "Score": analysis.get("score", 0),
                        "Sinal": f"{analysis.get('signal_icon', '')} {analysis.get('signal', '')}",
                        "Classificação": analysis.get("classification", "-"),
                        "Tendência": analysis.get("trend", "-"),
                        "Risco": analysis.get("risk", "-"),
                        "RSI": analysis.get("rsi", 0)
                    })
            except Exception:
                pass
            progress_bar.progress((i + 1) / len(assets_to_scan))
            time.sleep(0.03)

        status_text.text("Varredura concluída com sucesso!")
        
        if results_list:
            df_res = pd.DataFrame(results_list)
            df_res = df_res.sort_values(by="Score", ascending=False).reset_index(drop=True)
            df_top = df_res.head(top_n)

            st.markdown(f"### 🏆 Top {top_n} Maiores Pontuações no Mercado")
            st.dataframe(df_top, use_container_width=True)

            st.plotly_chart(create_scanner_summary_chart(df_top), use_container_width=True)
        else:
            st.warning("Não foi possível coletar dados para a lista selecionada.")

elif menu == "Sobre o Projeto":
    st.subheader("🚀 Sobre o InvestIA PRO")
    st.markdown("""
    O **InvestIA PRO** é uma plataforma institucional para inteligência de investimentos e análise quantitativa.
    """)
