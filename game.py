from connections import bot, NameForm
from aiogram import types
from constants import TOTAL_CUP_NUM, BLACK_IN


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
    # upd in db game status - forward
    pass


async def update_active_game(user_id: str, answer_data: str):
    # parse answer_data
    # get_active_game_data
    # update game data - steps or score
    # check if win or fail
    # some msg with score or with chosen cup
    # if win:
    # end_game
    # if fail:
    # end game
    # else:
    # new_game_iteration
    pass


async def send_cup_pictures():
    # random if_black_cup_in
    # if in -> get_pics(total_cup_num = TOTAL_CUP_NUM, black_in = BLACK_IN)
    pass


async def send_inline_buttons_to_choose(user_id, black: dict):
    # generate scores for basic cups
    # black {black_in: bool
    #        black_pos: int}
    # if black_in -> auto-fail
    # create buttons with text and hidden scores + UNIQUE KEY FOR BUTTON HANDLERS 'iter_button'
    # send buttons
    pass


async def new_game_iteration(user_id):
    # cups = send_cup_pictures  тут будут возвращаться значения баллы/.... того что мы нарандомили для отправки
    # send_inline_buttons_to_choose
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
    # TODO send pics to start game == new_game_iteration


async def end_game(user_id: str):
    """
    TODO change state and some support msg idk
    :param user_id:
    :return:
    """
    await NameForm.all_set_for_game.set()
    await bot.send_message(user_id, 'В следующий раз улов будет получше!!')
    # TODO end_active_game - change game status in db
    await send_start_game_button(user_id, 'Угон по расписанию')

