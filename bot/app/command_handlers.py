from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.bot_funcs import load_user, save_user_data
from bot.state import *

router = Router()


@router.message(Command('start'))
async def send_welcome(message: Message):
    user_id = message.from_user.id
    if not users.get(user_id):
        users[user_id] = load_user(user_id)

    user_states[user_id] = 'awaiting_test_start'
    await message.answer("Привет! Я бот для тестирования ваших знаний. Вы можете начать тест с помощью команды /test.")


@router.message(Command('stats'))
async def send_welcome(message: Message):
    user_id = message.from_user.id
    if not users.get(user_id):
        users[user_id] = load_user(user_id)

    user_states[user_id] = 'getting_info'
    await message.answer(users[user_id].stats())


@router.message(Command('clear'))
async def send_welcome(message: Message):
    user_id = message.from_user.id
    if not users.get(user_id):
        users[user_id] = load_user(user_id)

    user_states[user_id] = 'clearing'
    users[user_id].clear_data()
    save_user_data(users[user_id])
    await message.answer("Статистика удалена")


@router.message(Command('test'))
async def start_test(message: Message):
    user_id = message.from_user.id
    user_states[user_id] = 'awaiting_question_amount'
    await message.answer("На сколько вопросов вы хотите ответить?")


@router.message(lambda msg: user_states.get(msg.from_user.id) == 'awaiting_question_amount')
async def set_question_amount(message: Message):
    user_id = message.from_user.id
    if not users.get(user_id):
        users[user_id] = load_user(user_id)
    try:
        q_amount = int(message.text)
        if q_amount < 1:
            raise ValueError("Количество вопросов должно быть положительным числом.")

        users[user_id].start_test(q_amount=q_amount)
        user_states[user_id] = 'answering_questions'

        await ask_question(message, user_id)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.")


async def ask_question(message: Message, user_id):
    question = users[user_id].get_next_question()
    if question:
        await message.answer(question)
    else:
        await message.answer('Какая-то хуйня')


@router.message(lambda message: user_states.get(message.from_user.id) == 'answering_questions')
async def process_answer(message: Message):
    user_id = message.from_user.id

    users[user_id].answer_question(message.text)
    users[user_id].test.increment_question()

    if not users[user_id].test_completed():
        await ask_question(message, user_id)
    else:
        await message.answer(users[user_id].test.test_result())
        save_user_data(users[user_id])

