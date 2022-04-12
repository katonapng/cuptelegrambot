import logging
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from bottoken import token

bot = Bot(token)

dp = Dispatcher(bot, storage=MemoryStorage())

class NameForm(StatesGroup):
    await_name = State()


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

    await NameForm.await_name.set()



@dp.message_handler(commands="help")
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
                         "/help - get all available requests\n")


@dp.message_handler(content_types=['text'], state=NameForm.await_name)
async def name_getter(message: types.Message):
    """Function to handle random text messages.
    Echo message is sent back to user.
    Args:
        message (types.Message): message sent by the user.
    """
    # add name to db
    await bot.send_message(message.from_user.id,'Вы в группе прошмандовки лабы: ' + message.text)


@dp.message_handler(content_types=['text'])
async def echo_message(message: types.Message):
    """Function to handle random text messages.
    Echo message is sent back to user.
    Args:
        message (types.Message): message sent by the user.
    """
    await bot.send_message(message.from_user.id, message.text)



if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)