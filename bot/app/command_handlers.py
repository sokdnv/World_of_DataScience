from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from bot.funcs.bot_funcs import save_user_data
from bot.app.vars import users
from bot.funcs.bot_funcs import load_check
import bot.app.keyboards as kb

# роутер для передачи хэндлеров в основной скрипт
router = Router()


class UserState(StatesGroup):
    """
    Класс для обработки состояний юзера
    """
    choosing_test_type = State()
    awaiting_question_amount = State()
    answering = State()
    feedback = State()


@router.message(Command('start'))
async def send_welcome(message: Message):
    """Хэндлер команды /start"""
    user_id = message.from_user.id
    load_check(user_id)

    await message.answer(f"Привет *{message.from_user.first_name}*! Я бот для тестирования твоих знаний\n"
                         f"Ты можешь начать тест с помощью команды /test")


@router.message(Command('stats'))
async def show_stats(message: Message):
    """Хэндлер команды /stats"""
    user_id = message.from_user.id
    load_check(user_id)

    await message.answer(users[user_id].stats())


@router.message(Command('clear'))
async def clear_user_info(message: Message):
    """Хэндлер команды /clear"""
    user_id = message.from_user.id
    load_check(user_id)

    users[user_id].clear_data()
    save_user_data(users[user_id])
    await message.answer("Статистика удалена")


@router.message(Command('test'))
async def start_test(message: Message, state: FSMContext):
    """Хэндлер команды /test"""
    await state.set_state(UserState.choosing_test_type)
    await message.answer("Выбери тип тестирования", reply_markup=kb.test_type_kb)


@router.message(UserState.choosing_test_type)
async def set_test_type(message: Message, state: FSMContext):
    """Хэндлер выбора варианта тестирования"""
    user_id = message.from_user.id
    load_check(user_id)
    try:
        test_type = message.text
        if test_type == 'Блиц':
            users[user_id].start_blitz_test()
            await state.set_state(UserState.answering)
            await ask_question(message, user_id)
        elif test_type == 'Обычное':
            await state.set_state(UserState.awaiting_question_amount)
            await message.answer("На сколько вопросов вы хотите ответить?")
        else:
            raise ValueError('Ошибка выбора режима тестирования')

    except ValueError:
        await message.answer("Выбери корректный вариант")


@router.message(UserState.awaiting_question_amount)
async def set_test_q_amount(message: Message, state: FSMContext):
    """Хэндлер выбора количества вопросов в обычном тестировании"""
    user_id = message.from_user.id
    load_check(user_id)
    try:
        q_amount = int(message.text)
        if q_amount < 1:
            raise ValueError("Количество вопросов должно быть положительным числом.")

        users[user_id].start_basic_test(q_amount=q_amount)
        await state.set_state(UserState.answering)
        await ask_question(message, user_id)

    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.")


async def ask_question(message: Message, user_id):
    """Функция достающая следующий вопрос из теста"""
    question = users[user_id].get_next_question()
    await message.answer(question)


@router.message(UserState.answering)
async def process_answer(message: Message, state: FSMContext):
    """Хэндлер обрабатывающий ответ на тест"""
    user_id = message.from_user.id
    keyboard = kb.feedback_kb if not users[user_id].test_completed() else kb.final_q_kb

    await message.reply(users[user_id].answer_question(message.text), reply_markup=keyboard)
    await state.set_state(UserState.feedback)


@router.message(UserState.feedback)
async def user_choice_test(message: Message, state: FSMContext):
    """Хэндлер фидбэка или получения следующего вопроса"""
    user_id = message.from_user.id
    if message.text == 'Фидбэк':
        keyboard = kb.next_q_kb if not users[user_id].test_completed() else kb.finish_test_kb
        await message.answer(users[user_id].test.give_feedback(), reply_markup=keyboard, parse_mode=None)

    if message.text == 'Следующий вопрос':
        await state.set_state(UserState.answering)
        await ask_question(message, user_id)

    if message.text == 'Завершить тест':
        await message.answer(users[user_id].test.test_result())
        await state.clear()
        save_user_data(users[user_id])
