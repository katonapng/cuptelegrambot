from connections import bot, NameForm
from aiogram import types


async def get_active_game(user_id: str):
    """
    TODO create db select
    :param user_id:
    :return: game_id
    """
    return -1


async def end_active_game(user_id: str):
    """
    TODO
    :param user_id:
    :return: end game score
    """
    # game_id = get_active_game(user_id
    pass


async def send_start_game_button(user_id: str, message_text: str):
    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
    keyboard_markup.row(types.InlineKeyboardButton('Начать угон', callback_data='start_new_game'))

    await bot.send_message(user_id, message_text, reply_markup=keyboard_markup)


async def send_end_game_button(user_id: str, message_text: str):
    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
    keyboard_markup.row(types.InlineKeyboardButton('Закончить угон', callback_data='end_game'))

    await bot.send_message(user_id, message_text, reply_markup=keyboard_markup)


async def start_game(user_id: str):
    await NameForm.gaming.set()
    # TODO send smt
