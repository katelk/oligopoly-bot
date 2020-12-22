from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import TOKEN
from States import States
from db_all_rooms import Tbgames
from market import market

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
table_games = Tbgames()


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    table_games.new_user(message.from_user.id, message.chat.id)
    await message.answer("Это бот-игра, который моделирует рынок олигополии по Курно. Олигополия - тип рынка "
                         "несовершенной конкуренции, на котором функционирует небольшое количество фирм. В модели "
                         "олигополии по Курно фирмы одновременно выбирают свой объем продаж. На основе их выбора, "
                         "исходя из спроса потребителя, формируется цена на товар. Чем больше товара на рынке, "
                         "тем он менее ценный для потребителя, и наоборот.")
    await message.answer("Присоединиться к игре - /joingame")
    await message.answer("Создать новую комнату для игры - /newgame")
    await States.LOBBY.set()


@dp.message_handler(commands=['joingame'], state=States.LOBBY)
async def join_game(message: types.Message):
    await message.answer("Введите назание комнаты, к которой хотите присоединиться")
    await message.answer("Чтобы вернуться, напишите /lobby")
    await States.JOIN_GAME_NAME.set()


@dp.message_handler(state=States.JOIN_GAME_NAME, commands=['lobby'])
async def go_lobby_join(message: types.Message):
    await message.answer("Присоединиться к игре - /joingame")
    await message.answer("Создать новую комнату для игры - /newgame")
    await States.LOBBY.set()


@dp.message_handler(state=States.CREATING_NEW_GAME_NAME, commands=['lobby'])
async def go_lobby_new_game(message: types.Message):
    await message.answer("Присоединиться к игре - /joingame")
    await message.answer("Создать новую комнату для игры - /newgame")
    await States.LOBBY.set()


@dp.message_handler(state=States.JOIN_GAME_NAME)
async def join_game_name(message: types.Message):
    if table_games.check_existence(message.text):
        table_games.try_connect_to_room(message.from_user.id, message.text)
        await message.answer("Введите пароль для комнаты")
        await States.JOIN_GAME_PASSWORD.set()
    else:
        await message.answer("Комнаты с таким названием не существует. Введите другое название комнаты")


@dp.message_handler(state=States.JOIN_GAME_PASSWORD)
async def join_game_password(message: types.Message):
    room_name = table_games.get_room(message.from_user.id)
    if table_games.check_password(message.text, room_name):
        await message.answer("Теперь придумайте себе имя для игры")
        await States.CHOOSING_PLAYER_NAME.set()
    else:
        await message.answer("Неверный пароль. Попробуйте ещё раз")


@dp.message_handler(commands=['newgame'], state=States.LOBBY)
async def new_game(message: types.Message):
    await message.answer("Придумайте и напишите название для вашей комнаты")
    await message.answer("Чтобы вернуться, напишите /lobby")
    await States.CREATING_NEW_GAME_NAME.set()


@dp.message_handler(state=States.CREATING_NEW_GAME_NAME)
async def creating_game_name(message: types.Message):  # названия комнат не должны повторяться
    if not table_games.check_existence(message.text):  # проверяем существует ли комната с таким названием
        table_games.new_room(message.from_user.id, message.text)
        await message.answer("Теперь придумайте пароль для комнаты (более 5 символов)")
        await States.CREATING_NEW_GAME_PASSWORD.set()  # меняем состояние, пользователь выбирает пароль
    else:
        await message.answer("Такое имя комнаты уже есть. Придумайте другое название")


@dp.message_handler(state=States.CREATING_NEW_GAME_PASSWORD)
async def creating_game_password(message: types.Message):
    if len(message.text) >= 5:
        table_games.set_password(message.from_user.id, message.text)
        await message.answer("Теперь придумайте себе имя для игры")
        await States.CHOOSING_PLAYER_NAME.set()
    else:
        await message.answer("Пароль слишком короткий. Введите другой пароль")


@dp.message_handler(state=States.CHOOSING_PLAYER_NAME)
async def choosing_player_name(message: types.Message):
    room_name = table_games.get_room(message.from_user.id)
    if not table_games.name_existence(message.text, room_name):
        table_games.set_name(room_name, message.from_user.id, message.text)
        if table_games.how_much_players(room_name) == 3:  # изменить на 3
            table_games.next_step(room_name)
            for user_id in table_games.get_players(room_name):
                await bot.send_message(table_games.get_chat_id(user_id[0]), "Комната заполнена. Напишите Готов,"
                                                                            " чтобы начать игру")
                await States.WAITING_FOR_PLAYERS.set()
        else:
            await message.answer("Теперь ждите других игроков")
            await States.WAITING_FOR_PLAYERS.set()
    else:
        await message.answer("Такое имя игрока уже есть. Придумайте другое имя")


@dp.message_handler(state=States.WAITING_FOR_PLAYERS)
async def waiting(message: types.Message):
    if message.text == "готов" or message.text == "Готов":
        table_games.set_state(message.from_user.id, "answering")
        table_games.next_step_user(message.from_user.id)
        await message.answer("Итак, вы являетесь владельцем фирмы, которая производит товар X на рынке "
                             "олигополии. Помимо вашей фирмы, на рынке функционируют еще 2 фирмы. Игра проходит в 5 "
                             "циклов. Каждый игровой цикл вы должны выбирать, какое количество товаров будете "
                             "производить. На основе вашего выбора и выбора других фирм на рынке будет "
                             "формироваться цена на ваш товар X. После каждого цикла вам будет приходить сообщение "
                             "об итогах игрового цикла.")
        await message.answer("Введите, какое количество товара вы будете производить в данный игровой цикл")
        await States.PLAYING_ANSWERING.set()


@dp.message_handler(state=States.PLAYING_ANSWERING)
async def playing(message: types.Message):
    q = message.text
    if not q.isdigit() or '.' in q:
        await message.answer("Неккоректный тип данных. Введите целое число")
    else:
        q = int(q)
        room_name = table_games.get_room(message.from_user.id)
        table_games.set_quantity(message.from_user.id, q)
        table_games.set_state(message.from_user.id, "waiting")
        if table_games.check_all_states("waiting", room_name):
            values = table_games.get_values(room_name)
            result = market(values)  # result = {"user_id1": income1, "user_id2": income2, "user_id3": income3)}
            table_games.update_income(room_name, result)
            rating = table_games.get_rate(room_name)

            rate = "Рейтинг игроков:" + "\n"
            table_games.next_step(room_name)
            for name in rating:
                rate = rate + name + ": " + str(table_games.get_money(room_name, name)) + "\n"
            for user_id in table_games.get_players(room_name):
                income = result[user_id[0]]
                await bot.send_message(user_id[0], "Ваша прибыль за данный игровой цикл составила " + str(income))
                await bot.send_message(user_id[0], rate)
            for user_id in table_games.get_players(room_name):
                await bot.send_message(user_id[0], "Чтобы продолжить, напишите Дальше")
                await States.PLAYING_WAITING.set()

            # if table_games.get_step(room_name) == 6:
            #     for user_id in table_games.get_players(room_name):
            #         await bot.send_message(user_id[0], "Игра завершена. Победитель: " + rating[0])
        else:
            await message.answer("Дожидаемся ответа других игроков")
            await States.PLAYING_WAITING.set()


@dp.message_handler(state=States.PLAYING_WAITING)
async def waiting_for_others(message: types.Message):
    if message.text == "Дальше" or message.text == "дальше":
        room_name = table_games.get_room(message.from_user.id)
        if table_games.get_step(room_name) == 4:  # изменить на 6
            rating = table_games.get_rate(room_name)
            rate = "Рейтинг игроков:" + "\n"
            for name in rating:
                rate = rate + name + ": " + str(table_games.get_money(room_name, name)) + "\n"
            await message.answer("Игра завершена. Победитель: " + rating[0] + "\n")
            await message.answer(rate)
            table_games.delete_user(message.from_user.id, room_name)
            if table_games.how_much_players(room_name) == 0:
                table_games.delete_room(room_name)
            await message.answer("Присоединиться к игре - /joingame")
            await message.answer("Создать новую комнату для игры - /newgame")
            await States.LOBBY.set()
        else:
            table_games.next_step_user(message.from_user.id)
            table_games.set_state(message.from_user.id, "answering")
            await message.answer("Введите, какое количество товара вы будете производить в данный игровой цикл")
            await States.PLAYING_ANSWERING.set()


if __name__ == "__main__":
    executor.start_polling(dp)
