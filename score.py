def calcular_score(variacao):

    score = 50

    if variacao > 5:
        score += 40
    elif variacao > 2:
        score += 25
    elif variacao > 0:
        score += 10
    elif variacao < -5:
        score -= 40
    elif variacao < -2:
        score -= 25
    else:
        score -= 10

    score = max(0, min(100, score))

    if score >= 80:
        recomendacao = "🟢 Compra Forte"
    elif score >= 60:
        recomendacao = "🟡 Compra"
    elif score >= 40:
        recomendacao = "⚪ Neutro"
    else:
        recomendacao = "🔴 Venda"

    return score, recomendacao
