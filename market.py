def market(values: dict):  # values = {"user_id1": Q1, "user_id2": Q2, "user_id3": Q3)}
    players = values.keys()
    a = 300                 # Qd = a - bP
    b = 5                   # P = (a - Qd)/b
    Q = 0
    MC = 5
    result = {}
    for player in players:
        Q += values[player]
    if Q >= a:
        for player in players:
            result[player] = - values[player]*MC  # прибыль
    else:
        P = (a - Q)/b
        for player in players:
            result[player] = values[player] * (P - MC)

    return result  # result = {"user_id1": income1, "user_id2": income2, "user_id3": income3)}

