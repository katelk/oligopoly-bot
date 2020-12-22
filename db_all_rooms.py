import sqlite3


class Tbgames:
    def __init__(self):
        self.connection = sqlite3.connect('rooms.db', check_same_thread=False)
        cursor = self.connection.cursor()
        cursor.execute(''' CREATE TABLE IF NOT EXISTS games
                           (creator INTEGER,
                           room_name VARCHAR(20),
                           password VARCHAR(20),
                           n_players INTEGER,
                           step INTEGER
                           )''')
        cursor.execute(''' CREATE TABLE IF NOT EXISTS users_rooms
                                   (user_id INTEGER,
                                   chat_id INTEGER,
                                   room_name VARCHAR(20)
                                   )''')
        cursor.close()
        self.connection.commit()

    def new_user(self, user_id, chat_id):  # регистрация нового для бота пользователя
        cursor = self.connection.cursor()
        check = list(cursor.execute('''SELECT * FROM users_rooms WHERE user_id = ?''', (user_id,)))
        if not check:
            cursor.execute('''INSERT INTO users_rooms
                                  (user_id, chat_id, room_name)
                                  VALUES (?, ?, ?)''', (user_id, chat_id, ""))
        cursor.close()
        self.connection.commit()

    def try_connect_to_room(self, user_id, room_name):  # добавление нового игрока в комнату из \joingame
        cursor = self.connection.cursor()
        cursor.execute('''UPDATE users_rooms
                        SET room_name = ?
                        WHERE user_id = ?''', (room_name, user_id))
        cursor.close()
        self.connection.commit()

    def new_room(self, user_id, room_name):  # создание новой комнаты
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO games
                          (creator, room_name, password, n_players, step)
                          VALUES (?, ?, ?, ?, ?)''', (user_id, room_name, "", 0, 0))
        cursor.execute('''CREATE TABLE IF NOT EXISTS ''' + room_name +
                       ''' (user_id INTEGER,
                            name VARCHAR(20),
                            state VARCHAR(30),
                            step INTEGER,
                            q INTEGER,
                            money INTEGER
                           )''')
        self.try_connect_to_room(user_id, room_name)
        cursor.close()
        self.connection.commit()

    def check_password(self, password, room_name):
        cursor = self.connection.cursor()
        if password == list((cursor.execute('''SELECT password FROM games WHERE room_name = ?''', (room_name,))))[0][0]:
            return True
        return False

    def check_existence(self, room_name):  # проверка существует ли комнаты с таким названием
        cursor = self.connection.cursor()
        check = list(cursor.execute('''SELECT * FROM games WHERE room_name = ?''', (room_name,)))
        if not check:
            return False
        return True

    def set_password(self, user_id, password):  # установление пароля для комнаты
        cursor = self.connection.cursor()
        cursor.execute('''UPDATE games
                          SET password = ?
                          WHERE creator = ?''', (password, user_id))
        cursor.close()
        self.connection.commit()

    def get_room(self, user_id):  # функция возвращает название комнаты, в которой сейчас играет пользователь с user_id
        cursor = self.connection.cursor()
        return list((cursor.execute('''SELECT room_name FROM users_rooms WHERE user_id = ?''', (user_id,))))[0][0]

    def name_existence(self, name, room_name):
        cursor = self.connection.cursor()
        check = list(cursor.execute('''SELECT * FROM ''' + room_name + ''' WHERE name = ?''', (name,)))
        if not check:
            return False
        return True

    def how_much_players(self, room_name):
        cursor = self.connection.cursor()
        return list(cursor.execute('''SELECT n_players FROM games WHERE room_name = ?''', (room_name,)))[0][0]

    def set_name(self, room_name, user_id, name):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO ''' + room_name +
                       ''' (user_id, name, state, step, money)
                           VALUES (?, ?, ?, ?, ?)''', (user_id, name, "pre-playing", 0, 1000))
        n = self.how_much_players(room_name)
        cursor.execute('''UPDATE games
                          SET n_players = ?
                          WHERE room_name = ?''', (n+1, room_name))

        cursor.close()
        self.connection.commit()

    def get_players(self, room_name):
        cursor = self.connection.cursor()
        return list(cursor.execute('''SELECT user_id FROM ''' + room_name))

    def get_chat_id(self, user_id):
        cursor = self.connection.cursor()
        return list(cursor.execute('''SELECT chat_id FROM users_rooms WHERE user_id = ?''', (user_id,)))[0][0]

    def delete_user(self, user_id, room_name):
        cursor = self.connection.cursor()

        n = self.how_much_players(room_name)
        cursor.execute('''UPDATE games
                                  SET n_players = ?
                                  WHERE room_name = ?''', (n - 1, room_name))
        cursor.execute('''UPDATE users_rooms
                          SET room_name = ?
                          WHERE user_id = ?''', ("", user_id))
        cursor.close()
        self.connection.commit()

    def check_all_states(self, state, room_name):
        cursor = self.connection.cursor()
        step = list(cursor.execute('''SELECT step FROM games WHERE room_name = ?''', (room_name,)))[0][0]
        states_steps = list(cursor.execute('''SELECT state, step FROM ''' + room_name))
        for status_step in states_steps:
            if status_step[0] != state or status_step[1] != step:
                return False
        return True

    def set_quantity(self, user_id, q):
        cursor = self.connection.cursor()
        cursor.execute('''UPDATE ''' + self.get_room(user_id) +
                       ''' SET q = ?
                           WHERE user_id = ?''', (q, user_id))
        cursor.close()
        self.connection.commit()

    def set_state(self, user_id, state):
        cursor = self.connection.cursor()
        cursor.execute('''UPDATE ''' + self.get_room(user_id) +
                       ''' SET state = ?
                       WHERE user_id = ?''', (state, user_id))
        cursor.close()
        self.connection.commit()

    def get_step(self, room_name):
        cursor = self.connection.cursor()
        return list(cursor.execute('''SELECT step FROM games WHERE room_name = ?''', (room_name,)))[0][0]

    def next_step_user(self, user_id):
        cursor = self.connection.cursor()
        room_name = self.get_room(user_id)
        step = list(cursor.execute('''SELECT step FROM ''' + room_name + ''' WHERE user_id = ?''', (user_id,)))[0][0]
        cursor.execute('''UPDATE ''' + room_name +
                       ''' SET step = ?
                       WHERE user_id = ?''', (step + 1, user_id))
        cursor.close()
        self.connection.commit()

    def next_step(self, room_name):
        cursor = self.connection.cursor()
        step = self.get_step(room_name)
        cursor.execute('''UPDATE games
                          SET step = ?
                          WHERE room_name = ?''', (step + 1, room_name))
        cursor.close()
        self.connection.commit()

    def get_values(self, room_name):
        values = {}  # values = {"user_id1": Q1, "user_id2": Q2, "user_id3": Q3)}
        cursor = self.connection.cursor()
        for user_id in self.get_players(room_name):
            values[user_id[0]] = list(cursor.execute('''SELECT q FROM ''' + room_name +
                                                     ''' WHERE user_id = ?''', (user_id[0],)))[0][0]
        return values

    def update_income(self, room_name, result: dict):
        cursor = self.connection.cursor()
        for user_id in result.keys():
            money = list(cursor.execute('''SELECT money FROM ''' + room_name +
                                        ''' WHERE user_id = ?''', (user_id,)))[0][0]
            cursor.execute('''UPDATE ''' + room_name +
                           ''' SET money = ?
                               WHERE user_id = ?''', (money + result[user_id], user_id))
        cursor.close()
        self.connection.commit()

    def get_rate(self, room_name):
        cursor = self.connection.cursor()
        players = self.get_players(room_name)
        rating = []
        for user_id in players:
            rating.append(list(cursor.execute('''SELECT name FROM ''' + room_name +
                                              ''' WHERE user_id = ?''', (user_id[0],)))[0][0])
        rating.sort(key=lambda x: list(cursor.execute('''SELECT money FROM ''' + room_name +
                                                      ''' WHERE name = ?''', (x,)))[0][0], reverse=True)
        return rating

    def get_money(self, room_name, name):
        cursor = self.connection.cursor()
        money = list(cursor.execute('''SELECT money FROM ''' + room_name +
                                    ''' WHERE name = ?''', (name,)))[0][0]
        return money

    def delete_room(self, room_name):
        cursor = self.connection.cursor()
        cursor.execute('''DROP TABLE ''' + room_name)
        cursor.execute('''DELETE FROM games WHERE room_name = ?''', (room_name,))
        cursor.close()
        self.connection.commit()
