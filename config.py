"""
InvestIA PRO - Módulo de Configurações Globais
"""

DEFAULT_ASSETS = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBAS3.SA", "BBDC4.SA", "ABEV3.SA", "WEGE3.SA", "PRIO3.SA", "RENT3.SA", "SUZB3.SA"]

APP_TITLE = "InvestIA PRO — Análise Inteligente de Ativos"
PAGE_ICON = "📈"

SCORE_WEIGHTS = {
    "trend": 40,
    "rsi": 35,
    "volatility": 25
}

SECTOR_MAPPING = {
    "PETR4.SA": "Petróleo & Gás",
    "VALE3.SA": "Mineração",
    "ITUB4.SA": "Financeiro",
    "BBAS3.SA": "Financeiro",
    "BBDC4.SA": "Financeiro",
    "ABEV3.SA": "Bens de Consumo",
    "WEGE3.SA": "Bens de Capital",
    "PRIO3.SA": "Petróleo & Gás",
    "RENT3.SA": "Serviços",
    "SUZB3.SA": "Papel & Celulose"
}
