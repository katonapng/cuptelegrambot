from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from bottoken import token
from disk import get_pictures

from game import get_active_game, end_active_game

import psycopg2

conn = psycopg2.connect(dbname='postgres', user='bot',
                        password='bot', host='localhost')
cursor = conn.cursor()

bot = Bot(token)

dp = Dispatcher(bot, storage=MemoryStorage())

commands = ['/help', '/start']


class NameForm(StatesGroup):
    # waiting for user to enter his/her/... name
    await_name = State()
    # registered user, no active games == all set for a new game
    all_set_for_game = State()
    # registered user, active game
    gaming = State()


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    """Function to handle /start command.
    Greatings message and all available commands are sent
    to the user.
    Args:
        message (types.Message): message sent by the user.
    """
    await message.answer("Welcome To The 75th Annual Hunger Games!\n"
                         "Uh... I mean, wrong text, who gave me this?\n"
                         "Welcome to the CupGame, of course!\n"
                         "Let me dig up some useful information... "
                         "Just a sec")
    await cmd_help(message)
    await message.answer("Введи свое имя")

    await NameForm.await_name.set()


@dp.message_handler(content_types=['text'], state=NameForm.await_name)
async def name_getter(message: types.Message, state: FSMContext):
    """Function to handle random text messages.
    Echo message is sent back to user.
    Args:
        message (types.Message): message sent by the user.
        :param message:
        :param state:
    """
    user_id = message.from_user.id
    user_name = message.text

    if not user_exists(user_id):

        if any(command in user_name for command in commands):
            await bot.send_message(message.from_user.id, 'Это команды, а я хочу от тебя имя')
            return
        else:
            table_name = "cupbot.user"
            cursor.execute("insert into %s values (%%s, %%s)" % table_name, [user_id, user_name])
            conn.commit()
            await bot.send_message(message.from_user.id, 'Привет, ' + message.text + ', начнем игру?)')
            await NameForm.all_set_for_game.set()
    else:
        await bot.send_message(message.from_user.id, 'Привет??')
        await bot.send_message(message.from_user.id, 'Неси свои проигрыши гордо под своим первым никнеймом, '
                                                     'мелкий угонщик')

        # TODO after restarting bot
        # if no active_games -> state game
        # if active_games -> standart function end_game: stop prev game + change state to all_set_for_game
        if await get_active_game(message.from_user.id) == -1:  # no active games
            await NameForm.all_set_for_game.set()
        else:
            await end_active_game(message.from_user.id)

        # TODO check for same nickname as prev and create new shaming msg


@dp.message_handler(commands="help", state='*')
async def cmd_help(message: types.Message):
    """Function to handle /help command.
    Message with all available commands is sent
    to the user.
    Args:
        message (types.Message): message sent by the user.
    """
    await message.answer("Here you go, all the requests you can ask of me\n"
                         "If I'm in the mood, i shall answer you:\n"
                         "/start - begin interaction\n"
                         "/help - get all available requests\n"
                         "Помни - за тобой следят!")
    pic_path = get_pictures()[0]
    await bot.send_photo(message.chat.id, pic_path)


def user_exists(user_id: str):
    cursor.execute('select * from cupbot.user where id = %s', [str(user_id)])
    users = cursor.fetchall()
    if not users:
        return False
    return True


@dp.message_handler(content_types=['text'], state='*')
async def echo_message(message: types.Message):
    """Function to handle random text messages.
    Echo message is sent back to user.
    Args:
        message (types.Message): message sent by the user.
    """
    await bot.send_message(message.from_user.id, message.text)


if __name__ == "__main__":
    # Start bot
    executor.start_polling(dp, skip_updates=True)

    cursor.close()
    conn.close()
