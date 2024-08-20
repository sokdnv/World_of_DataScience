from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
import pandas as pd
import logging
import asyncio

from user import User


logging.basicConfig(level=logging.INFO)

API_TOKEN = 'ВСТАВЬ СЮДА КЛЮЧ'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

users = {}


@dp.message(Command('start'))
async def send_welcome(message: Message):
    await message.answer("Привет! Я бот для тестирования ваших знаний. Вы можете начать тест с помощью команды /test.")


@dp.message(Command('test'))
async def start_test(message: Message):
    user_id = message.from_user.id

    if user_id not in users:
        users[user_id] = User(user_id)

    users[user_id].start_test()

    await ask_question(message)


async def ask_question(message: Message):
    user_id = message.from_user.id
    user = users[user_id]

    question = user.get_next_question()
    if question:
        await message.answer(question)


@dp.message(lambda message: message.from_user.id in users)
async def process_answer(message: Message):
    user_id = message.from_user.id
    user = users[user_id]

    user.answer_question(message.text)
    user.test.increment_question()

    if not user.test_completed():
        await ask_question(message)
    else:
        await message.answer(f"Тест завершён! Вы ответили правильно на {user.get_score()} "
                             f"из {user.test_len()} вопросов.")
        del users[user_id]


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
