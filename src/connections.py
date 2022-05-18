import psycopg2
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

from src.bottoken import token

conn = psycopg2.connect(dbname='postgres', user='bot',
                        password='bot', host='localhost')
cursor = conn.cursor()

bot = Bot(token)
dp = Dispatcher(bot, storage=MemoryStorage())


class NameForm(StatesGroup):
    # waiting for user to enter his/her/... name
    await_name = State()
    # registered user, no active games == all set for a new game
    all_set_for_game = State()
    # registered user, active game
    gaming = State()
