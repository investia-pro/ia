def calcular_score(variacao):

    score = 50

    if variacao >= 5:
        score += 45
    elif variacao >= 3:
        score += 35
    elif variacao >= 1:
        score += 20
    elif variacao >= 0:
        score += 10
    elif variacao <= -5:
        score -= 45
    elif variacao <= -3:
        score -= 35
    elif variacao <= -1:
        score -= 20
    else:
        score -= 10

    score = max(0, min(100, score))

    if score >= 85:
        recomendacao = '🟢 Compra Forte'
    elif score >= 70:
        recomendacao = '🟡 Compra'
    elif score >= 50:
        recomendacao = '⚪ Neutro'
    else:
        recomendacao = '🔴 Venda'

    return score, recomendacao
