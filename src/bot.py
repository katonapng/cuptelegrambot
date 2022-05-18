from aiogram import executor, types
from aiogram.dispatcher.filters import Text

from src.connections import NameForm, bot, conn, cursor, dp
from src.game import (end_game, get_active_game_data, send_end_game_button,
                      send_start_game_button, start_game, update_active_game)

commands = ['/help', '/start']


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    """
    Function to handle /start command.
    Greetings message and all available commands are sent
    to the user. Nickname is requested from the user.
    :param message: types.Message, message sent by the user.
    :return:
    """

    await message.answer("Добро пожаловать на Ежегодный Съезд"
                         " Угонщиков Тар!\n"
                         "Хостит мероприятие лаборатория Биоинформатики"
                         " Политеха.. жесть, согласны\n"
                         "Сейчас придумаю правила, пожалуй, в этот раз не"
                         " во время игры. "
                         "Секу ждемс")
    await cmd_help(message)
    await message.answer("Придумай погоняло и отправляйся на промысел."
                         " Погоняло в студию:")

    await NameForm.await_name.set()


@dp.message_handler(content_types=['text'], state=NameForm.await_name)
async def name_getter(message: types.Message):
    """
    Function to get the nickname of the user, which he/she/... sends
    in reply to the request.
    :param message: types.Message, message sent by the user.
    :return:
    """

    user_id = message.from_user.id
    user_name = message.text

    if not await user_exists(user_id):

        if any(command in user_name for command in commands):
            await bot.send_message(
                message.from_user.id,
                'Это команды, а я хочу от тебя погоняло'
            )
            return
        else:
            table_name = "cupbot.user"
            cursor.execute(
                "insert into %s values (%%s, %%s)" % table_name,
                [user_id, user_name]
            )
            conn.commit()

            await NameForm.all_set_for_game.set()
            await send_start_game_button(
                message.from_user.id,
                'Привет, ' + message.text + ', начнем игру?)'
            )

    else:
        await bot.send_message(message.from_user.id, 'Привет??')
        await bot.send_message(
            message.from_user.id,
            'Неси свои проигрыши гордо под своим первым погонялом,'
            ' мелкий угонщик'
        )

        if not await get_active_game_data(message.from_user.id):
            await NameForm.all_set_for_game.set()
        else:
            await end_game(message.from_user.id)

        await send_start_game_button(
            message.from_user.id,
            'У тебя только один путь гордого самурая - угон кружек'
        )


@dp.message_handler(commands="help", state='*')
async def cmd_help(message: types.Message):
    """
    Function to handle /help command.
    Message with all available commands is sent
    to the user.
    :param message: types.Message, message sent by the user
    :return:
    """

    await message.answer("С координатором угонщиков диалог простой:\n"
                         "/start - начать угонную карьеру\n"
                         "/help - получить помощь тебе вряд ли удастся,"
                         " но можешь попробовать.\n")

    await message.answer("В лабе три главных правила:\n"
                         "1. За одну вылазку - один угон.\n"
                         "2. Количество вылазок ограничено.\n"
                         "3. Угони достаточно, чтобы успеть опубликоваться за"
                         " посланные свыше вылазки. \n\n"
                         "Бди - кружки координаторов священны"
                         " и неприкосновенны,"
                         " за угон такой -- сразу бан.\n"
                         "Помни - за тобой следят и демократии тут нет,"
                         " поэтому все как я хочу.")


@dp.callback_query_handler(
    Text(equals='start_new_game'),
    state=NameForm.all_set_for_game
)
async def inline_callback_handler_new_game(query: types.CallbackQuery):
    """
    Handler to manage start game inline button.
    :param query: types.CallbackQuery.
    :return:
    """

    # msg on top of the chat
    # always answer callback queries, even if you have nothing to say
    await query.answer('')
    await bot.delete_message(
        chat_id=query.from_user.id,
        message_id=query.message.message_id
    )
    await start_game(query.from_user.id)


@dp.callback_query_handler(Text(equals='end_game'), state=NameForm.gaming)
async def inline_callback_handler_end_game(query: types.CallbackQuery):
    """
    Handler to manage end game inline button.
    :param query: types.CallbackQuery.
    :return:
    """

    await query.answer('')
    await bot.delete_message(
        chat_id=query.from_user.id,
        message_id=query.message.message_id
    )
    await end_game(query.from_user.id)


@dp.callback_query_handler(Text(contains='iter_game'), state=NameForm.gaming)
async def inline_callback_handler_choose_cup(query: types.CallbackQuery):
    """
    Handler to manage end choose cup button.
    :param query: types.CallbackQuery.
    :return:
    """

    await query.answer('')

    await bot.delete_message(
        chat_id=query.from_user.id,
        message_id=query.message.message_id
    )
    answer_data = query.data
    await update_active_game(query.from_user.id, answer_data)


async def user_exists(user_id: str):
    """
    Function to check if a user already used out bot
    via his/her/... telegram id that we store in DB.
    :param user_id: str, user's id.
    :return:
    """

    cursor.execute('select * from cupbot.user where id = %s', [str(user_id)])
    users = cursor.fetchall()
    if not users:
        return False
    return True


@dp.message_handler(content_types=['text'], state=NameForm.all_set_for_game)
async def echo_message_nogame_state(message: types.Message):
    """
    Function to handle any text while in all_set_for_game State.
    Offers the user to start a new game.
    :param message: types.Message, message sent by the user.
    :return:
    """

    await send_start_game_button(
        message.from_user.id,
        'У тебя только один путь гордого самурая - угон кружек'
    )


@dp.message_handler(content_types=['text'], state=NameForm.gaming)
async def echo_message_game_state(message: types.Message):
    """
    Function to handle any text while in gaming State.
    Offers the user to finish his/her/... current game.
    :param message: types.Message, message sent by the user.
    :return:
    """

    await send_end_game_button(message.from_user.id, 'Угон не задался?')


@dp.callback_query_handler(Text(contains=''), state='*')
async def button_check(query: types.CallbackQuery):
    """
    Function to react to the user pressing invalid button
    for current state from previous conversation.
    :param query: types.CallbackQuery.
    :return:
    """

    await query.answer('')
    await bot.send_message(query.from_user.id, 'Погоди, ты не туда тыкаешь')


@dp.message_handler(content_types=['text'], state='*')
async def echo_message(message: types.Message):
    """
    Function to react to the user sending us the text,
    which previous handlers didn't catch. Just echoes it.
    :param message: types.Message, message sent by the user.
    :return:
    """

    await bot.send_message(message.from_user.id, message.text)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
    cursor.close()
    conn.close()
