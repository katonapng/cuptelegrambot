from connections import bot, NameForm
from aiogram import types


async def get_active_game_data(user_id: str):
    """
    TODO create db select to find game id via user id
    :param user_id:
    :return: game_id .... dict with game data
    """
    return {}  # empty dict


async def end_active_game(user_id: str):
    """
    TODO changes in db and some stat msg mb
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
    await bot.send_message(user_id, 'Дэмн, удачи!!')
    # TODO send pics to start game


async def end_game(user_id: str):
    """
    TODO change state and some support msg idk
    :param user_id:
    :return:
    """
    await NameForm.all_set_for_game.set()
    await bot.send_message(user_id, 'В следующий раз улов будет получше!!')
    # TODO end_active_game
    await send_start_game_button(user_id, 'Угон по расписанию')

