import random

from connections import bot, NameForm
from aiogram import types
from constants import TOTAL_CUP_NUM, BLACK_IN, THRESHOLD_STEP, THRESHOLD_SCORE, BLACK_IN_PROBABILITY,\
                      MIN_SCORE_FOR_CUP, MAX_SCORE_FOR_CUP
from connections import conn, cursor

from disk import get_pictures


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


async def send_cup_pictures(user_id):
    """
    Send pics and return scores and info about presence of The Black Cup
    :param user_id:
    :return: scores, black_info
    """
    # TODO: randomize black cup position (rn its always the last one, if any)

    black_in = random.random() < BLACK_IN_PROBABILITY
    # get randomized set of cups
    chosen_files = await get_pictures(TOTAL_CUP_NUM, black_in=black_in)  # [] of links
    # randomize scores for the cups (NB: if black_in, the last one is black)
    scores = [random.randint(MIN_SCORE_FOR_CUP, MAX_SCORE_FOR_CUP + 1) for _ in range(TOTAL_CUP_NUM)]

    await bot.send_media_group(user_id, chosen_files)
    black_info = {"black_in": black_in, "black_pos": TOTAL_CUP_NUM - 1}
    return scores, black_info


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
    scores, black_info = await send_cup_pictures(user_id)
    await send_inline_buttons_to_choose(user_id, black_info)


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
    await create_game_in_db(user_id)
    # new_game_iteration
    # TODO send cups and inline keyboard to select one of them
    # TODO send pics to start game == new_game_iteration


async def create_game_in_db(user_id: str):
    """
    Initialize game
    :param user_id:
    :return:
    """
    table_name = "cupbot.game"
    cursor.execute(
        "insert into %s (user_id, curr_score, step_count, is_active) values (%%s, %%s, %%s, %%s)" % table_name,
        [user_id, 0, 0, True])
    conn.commit()


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

