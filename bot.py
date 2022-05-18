from aiogram import executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from disk import get_pictures
from game import get_active_game_data, end_active_game, send_start_game_button, \
    send_end_game_button, start_game, end_game, update_active_game
from connections import conn, cursor, bot, dp, NameForm

commands = ['/help', '/start']


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    """Function to handle /start command.
    Greatings message and all available commands are sent
    to the user.
    Args:
        message (types.Message): message sent by the user.
    """
    await message.answer("Добро пожаловать на Ежегодный Съезд Угонщиков Тар!\n"
                         "Хостит мероприятие лаборатория Биоинформатики Политеха.. жесть, согласны\n"
                         "Сейчас придумаю правила, пожалуй, в этот раз не во время игры. "
                         "Секу ждемс")
    await cmd_help(message)
    await message.answer("Придумай погоняло и отправляйся на промысел. Погоняло в студию:")

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
            await bot.send_message(message.from_user.id, 'Это команды, а я хочу от тебя погоняло')
            return
        else:
            table_name = "cupbot.user"
            cursor.execute("insert into %s values (%%s, %%s)" % table_name, [user_id, user_name])
            conn.commit()

            await NameForm.all_set_for_game.set()
            await send_start_game_button(message.from_user.id, 'Привет, ' + message.text + ', начнем игру?)')

    else:
        await bot.send_message(message.from_user.id, 'Привет??')
        await bot.send_message(message.from_user.id, 'Неси свои проигрыши гордо под своим первым погонялом, '
                                                     'мелкий угонщик')

        # TODO after restarting bot
        # if no active_games -> state game
        # if active_games -> standart function end_game: stop prev game + change state to all_set_for_game
        if not await get_active_game_data(message.from_user.id):  # no active games  TODO check for empty dict
            await NameForm.all_set_for_game.set()
        else:
            await end_game(message.from_user.id)

        # TODO check for same nickname as prev and create new shaming msg


@dp.message_handler(commands="help", state='*')
async def cmd_help(message: types.Message):
    """Function to handle /help command.
    Message with all available commands is sent
    to the user.
    Args:
        message (types.Message): message sent by the user.
    """
    await message.answer("С координатором угонщиков диалог простой:\n"
                         "/start - начать угонную карьеру\n"
                         "/help - получить помощь тебе вряд ли удастся, но можешь попробовать.\n")

    await message.answer("В лабе три главных правила:\n"
                         "1. За одну вылазку - один угон.\n"
                         "2. Количество вылазок ограничено.\n"
                         "3. Угони достаточно, чтобы успеть опубликоваться за посланные свыше вылазки. \n\n"
                         "Бди - кружки координаторов священны и неприкосновенны, за угон такой -- сразу бан.\n"
                         "Помни - за тобой следят и демократии тут нет, поэтому все как я хочу.")


@dp.callback_query_handler(Text(equals='start_new_game'), state=NameForm.all_set_for_game)
async def inline_kb_answer_callback_handler_new_game(query: types.CallbackQuery):
    # always answer callback queries, even if you have nothing to say
    await query.answer('')  # месседж вверху всплывающий, можно чет закинуть))
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)

    await start_game(query.from_user.id)


@dp.callback_query_handler(Text(equals='end_game'), state=NameForm.gaming)
async def inline_kb_answer_callback_handler_end_game(query: types.CallbackQuery):
    # always answer callback queries, even if you have nothing to say
    # TODO end game
    await query.answer('')  # месседж вверху всплывающий, можно чет закинуть))
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await end_game(query.from_user.id)


@dp.callback_query_handler(Text(contains='iter_game'), state=NameForm.gaming)
async def inline_kb_answer_callback_handler_choose_cup(query: types.CallbackQuery):
    # always answer callback queries, even if you have nothing to say
    await query.answer('')  # месседж вверху всплывающий, можно чет закинуть))

    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    answer_data = query.data
    await update_active_game(query.from_user.id, answer_data)


def user_exists(user_id: str):
    cursor.execute('select * from cupbot.user where id = %s', [str(user_id)])
    users = cursor.fetchall()
    if not users:
        return False
    return True


@dp.message_handler(content_types=['text'], state=NameForm.all_set_for_game)
async def echo_message_nogame_state(message: types.Message, state: FSMContext):
    """Function to handle random text messages in all_set_for_gae state
    Start new game message is sent back to user.
    Args:
        message (types.Message): message sent by the user.
        :param message:
        :param state:
    """
    await send_start_game_button(message.from_user.id, 'У тебя только один путь гордого самурая - угон кружек')


@dp.message_handler(content_types=['text'], state=NameForm.gaming)
async def echo_message_game_state(message: types.Message, state: FSMContext):
    """Function to handle random text messages in all_set_for_gae state
    Start new game message is sent back to user.
    Args:
        message (types.Message): message sent by the user.
        :param message:
        :param state:
    """
    await send_end_game_button(message.from_user.id, 'Угон не задался?')


@dp.callback_query_handler(Text(contains=''), state='*')
async def button_check(query: types.CallbackQuery):
    # always answer callback queries, even if you have nothing to say
    # TODO end game
    await query.answer('')  # месседж вверху всплывающий, можно чет закинуть))
    await bot.send_message(query.from_user.id, 'Погоди, ты не туда тыкаешь')


@dp.message_handler(content_types=['text'], state='*')
async def echo_message(message: types.Message, state: FSMContext):
    """Function to handle random text messages.
    Echo message is sent back to user.
    Args:
        message (types.Message): message sent by the user.
        :param state:
    """
    await bot.send_message(message.from_user.id, message.text)


if __name__=="__main__":
    # Start bot
    executor.start_polling(dp, skip_updates=True)

    cursor.close()
    conn.close()
