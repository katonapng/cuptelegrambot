import random

from aiogram import types

from src.connections import NameForm, bot, conn, cursor
from src.constants import (BLACK_IN_PROBABILITY, MAX_SCORE_FOR_CUP,
                           MIN_SCORE_FOR_CUP, THRESHOLD_SCORE, THRESHOLD_STEP,
                           TOTAL_CUP_NUM)
from src.disk import get_pictures


async def get_active_game_data(user_id: str):
    """
    :param user_id:
    :return: dict
    """
    cursor.execute(
        'select * from cupbot.game '
        'where user_id = %s and is_active = %s',
        [str(user_id), True]
    )
    game = cursor.fetchall()

    if not game:
        return {}

    game_id, user_id, cur_score, step_count, is_active = game[0]
    game_data = {'curr_score': int(cur_score),
                 'step_count': int(step_count),
                 'game_id': int(game_id)}
    return game_data


async def end_active_game(user_id: str):
    """
    :param user_id:
    :return: end game score
    """
    # game_id = get_active_game(user_id
    # upd in db game status - forward
    table_name = "cupbot.game"
    cursor.execute(
        "update %s set is_active = %%s"
        " where user_id = %%s and is_active = %%s" % table_name,
        [False, user_id, True]
    )
    conn.commit()


async def upd_game_db_rec(game_id: int, new_score: int, new_step_count: int):
    table_name = "cupbot.game"
    cursor.execute(
        "update %s set curr_score = %%s,"
        " step_count = %%s where ID = %%s" % table_name,
        [new_score, new_step_count, game_id]
    )
    conn.commit()


async def update_active_game(user_id: str, answer_data: str):
    game_data = await get_active_game_data(user_id)
    parsed_data = answer_data.split()
    cup_score = int(parsed_data[-2])
    cup_is_black = int(parsed_data[-1])

    game_stats = await check_end_game(game_data, cup_score, cup_is_black)
    await bot.send_message(user_id, game_stats['msg'])

    if game_stats['game_is_ended']:
        await end_game(user_id)
    else:
        await upd_game_db_rec(
            game_data['game_id'],
            game_stats['new_score'],
            game_stats['new_step_count']
        )
        await new_game_iteration(user_id)


async def check_end_game(game_data: dict, cup_score: int, cup_is_black: int):
    '''
    :param cup_is_black:
    :param cup_score:
    :param game_data:
    :return: boolean
    '''

    new_score = game_data['curr_score'] + cup_score
    new_step_count = game_data['step_count'] + 1

    if cup_is_black:
        msg = 'Поздравляю, ты жестко напоролся на императорскую кружку. ' \
              '\nС такими заслугами расплата не за горами, удачи с ' \
              'угоном в других ботах.'

        return {'game_is_ended': True,
                'msg': msg}

    elif new_score >= THRESHOLD_SCORE:
        msg = 'Поздравляю, ты обчистил лабу,' \
              ' отчисление не за горами и это победа!!. \n' +\
              '\nСчет составил: ' + str(new_score) +\
              '\nКоличество совершенных угонов: ' + str(new_step_count)

        return {'game_is_ended': True,
                'msg': msg}

    elif new_step_count == THRESHOLD_STEP:
        msg = 'Поздравляю, столько угонов (аж ' + str(new_step_count) +\
              ') и ни одного достойного упоминания.' +\
              '\nЭто не победа и вообще сочувствую,' \
              ' удачи в следующих угонах, лошара ;-)'

        return {'game_is_ended': True,
                'msg': msg}

    else:
        msg = 'В этот раз тебя никто не поймал, продолжай гонять дальше.' \
              '\n\nТекущий счет: ' + str(new_score) + ', а для победы надо ' \
              + str(THRESHOLD_SCORE) + '\nУгонов совершено: '\
              + str(new_step_count) + ', а через ' \
              + str(THRESHOLD_STEP - new_step_count)\
              + ' тебя прижучат.'

        return {'game_is_ended': False,
                'msg': msg,
                'new_score': new_score,
                'new_step_count': new_step_count}


async def send_cup_pictures(user_id):
    """
    Send pics and return scores and info about presence of The Black Cup
    :param user_id:
    :return: scores, black_info
    """
    await bot.send_message(
        user_id,
        'Жди, кружки уже в пути!! Тебе надо будет выбрать свою жертву, ловец!'
    )
    black_in = random.random() < BLACK_IN_PROBABILITY
    # get randomized set of cups
    chosen_files = await get_pictures(
        TOTAL_CUP_NUM,
        black_in=black_in
    )
    # randomize scores for the cups (NB: if black_in, the last one is black)
    scores = [
        random.randint(MIN_SCORE_FOR_CUP, MAX_SCORE_FOR_CUP + 1)
        for _ in range(TOTAL_CUP_NUM)
    ]

    for file in chosen_files:
        await bot.send_photo(user_id, file)

    black_pos = TOTAL_CUP_NUM - 1
    black_mask = [1 if i == black_pos and black_in else 0
                  for i in range(TOTAL_CUP_NUM)
                  ]
    return scores, black_mask


async def send_inline_buttons_to_choose(user_id, scores, black_mask: list):
    nums = ['первую!', 'вторую!', 'третью!']
    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)

    text_and_data = [
        ("Угнать " + nums[i],
         "iter_game " + str(i) + " "
         + str(scores[i]) + " " + str(black_mask[i])
         )
        for i in range(TOTAL_CUP_NUM)
    ]
    row_btns = (
        types.InlineKeyboardButton(text, callback_data=data)
        for text, data in text_and_data
    )
    keyboard_markup.row(*row_btns)

    await bot.send_message(
        user_id,
        "Выбирай свою цель, юный угонщик!",
        reply_markup=keyboard_markup
    )


async def new_game_iteration(user_id):
    scores, black_info = await send_cup_pictures(user_id)
    await send_inline_buttons_to_choose(user_id, scores, black_info)


async def send_start_game_button(user_id: str, message_text: str):
    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
    keyboard_markup.row(
        types.InlineKeyboardButton(
            'Начать угон',
            callback_data='start_new_game')
    )

    await bot.send_message(user_id, message_text, reply_markup=keyboard_markup)


async def send_end_game_button(user_id: str, message_text: str):
    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
    keyboard_markup.row(
        types.InlineKeyboardButton(
            'Закончить угон',
            callback_data='end_game'
        )
    )

    await bot.send_message(user_id, message_text, reply_markup=keyboard_markup)


async def start_game(user_id: str):
    await NameForm.gaming.set()
    await bot.send_message(user_id, 'Дэмн, удачи!!')
    await create_game_in_db(user_id)
    await new_game_iteration(user_id)
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
        "insert into %s (user_id, curr_score, step_count, is_active)"
        " values (%%s, %%s, %%s, %%s)" % table_name,
        [user_id, 0, 0, True]
    )
    conn.commit()


async def end_game(user_id: str):
    """
    TODO change state and some support msg idk
    :param user_id:
    :return:
    """
    await bot.send_message(user_id, 'Угонные победы ждут тебя!!')
    await end_active_game(user_id)

    await NameForm.all_set_for_game.set()
    await send_start_game_button(user_id, 'Угон по расписанию')
