"""
InvestIA PRO — Aplicação Principal Streamlit (Fase 3.0.7)
"""
import streamlit as st
import pandas as pd
import time
import sys
from pathlib import Path

# Adiciona o diretório atual ao sys.path para evitar ImportError em subpastas no Streamlit Cloud
current_dir = Path(__file__).parent.resolve()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from config import DEFAULT_ASSETS, APP_TITLE, PAGE_ICON
    from market import fetch_asset_data
    from analysis import analyze_asset
    from charts import create_price_chart, create_scanner_summary_chart
    from utils import format_currency, format_percent
except ImportError:
    from .config import DEFAULT_ASSETS, APP_TITLE, PAGE_ICON
    from .market import fetch_asset_data
    from .analysis import analyze_asset
    from .charts import create_price_chart, create_scanner_summary_chart
    from .utils import format_currency, format_percent

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📈 InvestIA PRO — Análise de Mercado & Scanner")
st.caption("Fase 3.0.7 — Integração de Dashboard Executivo e Scanner Multi-Ativos")

# Sidebar - Navegação
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
            mkt_data = fetch_asset_data(ticker_input)
            
            if not mkt_data["is_valid"]:
                st.error(f"Erro: {mkt_data['error']}")
            else:
                res = analyze_asset(mkt_data)
                
                # Metric Cards
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("Preço Atual", format_currency(res["price"]), delta=format_percent(res["change_percent"]))
                c2.metric("Score InvestIA", f"{res['score']} / 100", delta=res["signal"])
                c3.metric("Classificação", res["classification"])
                c4.metric("Tendência", res["trend"])
                c5.metric("Nível de Risco", res["risk"])

                st.markdown("---")

                # Resumo Executivo & Recomendações
                col_left, col_right = st.columns([1, 1])

                with col_left:
                    st.markdown("### 📋 Resumo Executivo")
                    st.info(res["executive_summary"])
                    st.markdown(f"**Recomendação:** {res['recommendation']}")

                    st.markdown("#### Justificativas do Sinal:")
                    for r in res["reasons"]:
                        st.write(f"• {r}")

                with col_right:
                    st.markdown("### 📊 Decomposição do Score")
                    b = res["breakdown"]
                    st.write(f"• **Tendência:** {b['trend_score']} / 40 pts")
                    st.write(f"• **RSI:** {b['rsi_score']} / 35 pts")
                    st.write(f"• **Volatilidade/Risco:** {b['volatility_score']} / 25 pts")
                    
                    st.markdown("#### Detalhes Técnicos:")
                    st.write(f"• **RSI (14):** {res['rsi']} ({res['rsi_status']})")
                    st.write(f"• **MA 21:** {format_currency(res['ma21'])}")
                    st.write(f"• **MA 200:** {format_currency(res['ma200'])}")
                    st.write(f"• **Volatilidade Anual:** {res['volatility']:.2f}%")

                st.markdown("---")

                # Gráfico
                st.plotly_chart(create_price_chart(res), use_container_width=True)

elif menu == "Scanner de Mercado":
    st.subheader("🎯 Scanner de Oportunidades Automático")
    st.write("Análise em lote de ativos selecionados para identificação rápida das melhores pontuações.")

    selected_assets = st.multiselect(
        "Selecione a lista de ativos para escanear:",
        options=["PETR4", "VALE3", "ITUB4", "BBAS3", "BBDC4", "ABEV3", "WEGE3", "PRIO3", "RENT3", "SUZB3"],
        default=["PETR4", "VALE3", "ITUB4", "BBAS3", "WEGE3"]
    )

    if st.button("INICIAR SCANNER", type="primary"):
        results_list = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, symbol in enumerate(selected_assets):
            status_text.text(f"Escaneando {symbol} ({i+1}/{len(selected_assets)})...")
            m_data = fetch_asset_data(symbol)
            if m_data["is_valid"]:
                analysis = analyze_asset(m_data)
                results_list.append({
                    "Ativo": analysis["asset"],
                    "Preço (R$)": analysis["price"],
                    "Var. (%)": analysis["change_percent"],
                    "Score": analysis["score"],
                    "Sinal": f"{analysis['signal_icon']} {analysis['signal']}",
                    "Classificação": analysis["classification"],
                    "Tendência": analysis["trend"],
                    "Risco": analysis["risk"],
                    "RSI": analysis["rsi"]
                })
            progress_bar.progress((i + 1) / len(selected_assets))
            time.sleep(0.1)

        status_text.text("Scan concluído com sucesso!")
        
        if results_list:
            df_res = pd.DataFrame(results_list)
            df_res = df_res.sort_values(by="Score", ascending=False).reset_index(drop=True)

            st.markdown("### 🏆 Ranking de Oportunidades")
            st.dataframe(df_res, use_container_width=True)

            st.plotly_chart(create_scanner_summary_chart(df_res), use_container_width=True)
        else:
            st.warning("Nenhum ativo pôde ser escaneado com sucesso.")

elif menu == "Sobre o Projeto":
    st.subheader("🚀 Sobre o InvestIA PRO")
    st.markdown("""
    O **InvestIA PRO** é um sistema modular em desenvolvimento para análise quantitativa e qualitativa do mercado financeiro.
    """)
