from aiogram.dispatcher.filters.state import StatesGroup, State


class States(StatesGroup):
    LOBBY = State()
    CREATING_NEW_GAME_NAME = State()
    CREATING_NEW_GAME_PASSWORD = State()
    CHOOSING_PLAYER_NAME = State()
    WAITING_FOR_PLAYERS = State()
    JOIN_GAME_NAME = State()
    JOIN_GAME_PASSWORD = State()
    PLAYING_ANSWERING = State()
    PLAYING_WAITING = State()
    PLAYING_READY = State()
