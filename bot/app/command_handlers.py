from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from bot.funcs.bot_funcs import save_user_data
from bot.util.state import users
from bot.funcs.bot_funcs import load_check

router = Router()


class TestingState(StatesGroup):
    choosing_test_type = State()
    awaiting_question_amount = State()
    answering = State()


@router.message(Command('start'))
async def send_welcome(message: Message):
    user_id = message.from_user.id
    load_check(user_id)

    await message.answer(f"Привет {message.from_user.first_name}! Я бот для тестирования твоих знаний. "
                         f"Ты можешь начать тест с помощью команды /test.")


@router.message(Command('stats'))
async def send_welcome(message: Message):
    user_id = message.from_user.id
    load_check(user_id)

    await message.answer(users[user_id].stats())


@router.message(Command('clear'))
async def send_welcome(message: Message):
    user_id = message.from_user.id
    load_check(user_id)

    users[user_id].clear_data()
    save_user_data(users[user_id])
    await message.answer("Статистика удалена")


@router.message(Command('test'))
async def start_test(message: Message, state: FSMContext):
    await state.set_state(TestingState.choosing_test_type)
    await message.answer("Выбери тип тестирования. (Обычное / Блиц)")


@router.message(TestingState.choosing_test_type)
async def set_test(message: Message, state: FSMContext):
    user_id = message.from_user.id
    load_check(user_id)
    try:
        test_type = message.text.lower()
        if test_type == 'блиц':
            users[user_id].start_test(test_type='blitz')
            await state.set_state(TestingState.answering)
            await ask_question(message, user_id)
        elif test_type == 'обычное':
            await state.set_state(TestingState.awaiting_question_amount)
            await message.answer("На сколько вопросов вы хотите ответить?")
        else:
            raise ValueError('Ошибка выбора режима тестирования')

    except ValueError:
        await message.answer("Выбери корректный вариант")


@router.message(TestingState.awaiting_question_amount)
async def set_test(message: Message, state: FSMContext):
    user_id = message.from_user.id
    load_check(user_id)
    try:
        q_amount = int(message.text)
        if q_amount < 1:
            raise ValueError("Количество вопросов должно быть положительным числом.")

        users[user_id].start_test(test_type='basic', q_amount=q_amount)
        await state.set_state(TestingState.answering)
        await ask_question(message, user_id)

    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.")


async def ask_question(message: Message, user_id):
    question = users[user_id].get_next_question()
    await message.answer(question)


@router.message(TestingState.answering)
async def process_answer(message: Message, state: FSMContext):
    user_id = message.from_user.id

    users[user_id].answer_question(message.text)
    users[user_id].test.increment_question()

    if not users[user_id].test_completed():
        await ask_question(message, user_id)
    else:
        await message.answer(users[user_id].test.test_result())
        await state.clear()
        save_user_data(users[user_id])
