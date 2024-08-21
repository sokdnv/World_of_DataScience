from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from bot.funcs.bot_funcs import load_user, save_user_data
from bot.util.state import users

router = Router()


class TestingState(StatesGroup):
    awaiting_question_amount = State()
    answering = State()


@router.message(Command('start'))
async def send_welcome(message: Message):
    user_id = message.from_user.id
    if not users.get(user_id):
        users[user_id] = load_user(user_id)

    await message.answer("Привет! Я бот для тестирования ваших знаний. Вы можете начать тест с помощью команды /test.")


@router.message(Command('stats'))
async def send_welcome(message: Message):
    user_id = message.from_user.id
    if not users.get(user_id):
        users[user_id] = load_user(user_id)

    await message.answer(users[user_id].stats())


@router.message(Command('clear'))
async def send_welcome(message: Message):
    user_id = message.from_user.id
    if not users.get(user_id):
        users[user_id] = load_user(user_id)

    users[user_id].clear_data()
    save_user_data(users[user_id])
    await message.answer("Статистика удалена")


@router.message(Command('test'))
async def start_test(message: Message, state: FSMContext):
    await state.set_state(TestingState.awaiting_question_amount)
    await message.answer("На сколько вопросов вы хотите ответить?")


@router.message(TestingState.awaiting_question_amount)
async def set_question_amount(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if not users.get(user_id):
        users[user_id] = load_user(user_id)
    try:
        q_amount = int(message.text)
        if q_amount < 1:
            raise ValueError("Количество вопросов должно быть положительным числом.")

        users[user_id].start_test(q_amount=q_amount)
        await state.set_state(TestingState.answering)

        await ask_question(message, user_id)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.")


async def ask_question(message: Message, user_id):
    question = users[user_id].get_next_question()
    if question:
        await message.answer(question)
    else:
        await message.answer('Какая-то хуйня')


@router.message(TestingState.answering)
async def process_answer(message: Message):
    user_id = message.from_user.id

    users[user_id].answer_question(message.text)
    users[user_id].test.increment_question()

    if not users[user_id].test_completed():
        await ask_question(message, user_id)
    else:
        await message.answer(users[user_id].test.test_result())
        save_user_data(users[user_id])
