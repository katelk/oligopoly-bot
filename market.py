import random

def market(values: dict, a, b, MC):  # values = {"user_id1": Q1, "user_id2": Q2, "user_id3": Q3)}
    players = values.keys()
    # a = 300                 # Qd = a - bP
    # b = 5                   # P = (a - Qd)/b
    Q = 0
    # MC = 5
    result = {}
    for player in players:
        Q += values[player]
    if Q >= a:
        for player in players:
            result[player] = - round(values[player]*MC, 1)  # прибыль
    else:
        P = (a - Q)/b
        for player in players:
            result[player] = round(values[player] * (P - MC), 1)

    return result  # result = {"user_id1": income1, "user_id2": income2, "user_id3": income3)}

def set_params():
    a = random.randint(200, 500)
    b = random.randint(5, 20)
    mc = a/b * random.choice([0.2, 0.25, 0.3, 0.35])
    return (a, b, mc)
