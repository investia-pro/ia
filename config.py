"""
InvestIA PRO
Configurações globais

Versão: 0.5.3 Stable
"""

# ======================================
# Aplicação
# ======================================

APP_NAME = "InvestIA PRO"
VERSION = "0.5.3 Stable"

PAGE_TITLE = "InvestIA PRO"
PAGE_ICON = "📈"

LAYOUT = "wide"

# ======================================
# Mercado
# ======================================

DEFAULT_PERIOD = "1y"

CACHE_TTL = 300

MARKET_SUFFIX = ".SA"

# ======================================
# Indicadores
# ======================================

RSI_PERIOD = 14

SHORT_MA = 21

LONG_MA = 200

VOLATILITY_WINDOW = 21

# ======================================
# Classificação
# ======================================

BUY_SCORE = 3

SELL_SCORE = -3

# ======================================
# RSI
# ======================================

RSI_OVERSOLD = 30

RSI_OVERBOUGHT = 70

# ======================================
# Interface
# ======================================

MAX_HISTORY = 500

SHOW_VOLUME = True

SHOW_GRID = True

THEME = "plotly_white"
