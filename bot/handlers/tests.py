import random
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.funcs.vars import users
from bot.funcs.bot_funcs import load_check, save_user_data
import bot.keyboards as kb
from bot.handlers.user_state import UserState

# роутер для передачи хэндлеров в основной скрипт
router = Router()


@router.message(Command('test'))
async def start_test(message: Message):
    """Хэндлер команды /test"""
    await message.answer("Выбери тип тестирования", reply_markup=kb.inline.test_choice_kb)


@router.callback_query(lambda callback_query: callback_query.data in ['blitz_test', 'basic_test'])
async def set_test_type(callback_query: CallbackQuery, state: FSMContext):
    """Хэндлер выбора варианта тестирования"""
    user_id = callback_query.from_user.id
    await load_check(user_id)

    test_type = callback_query.data
    if test_type == 'blitz_test':
        users[user_id].start_blitz_test()
        await callback_query.message.edit_reply_markup(reply_markup=None)
        await state.set_state(UserState.blitz_test)
        await ask_question_blitz(callback_query.message, user_id)
    elif test_type == 'basic_test':
        await state.set_state(UserState.awaiting_question_amount)
        await callback_query.message.edit_text("На сколько вопросов вы хотите ответить?")


@router.message(UserState.awaiting_question_amount)
async def set_test_q_amount(message: Message, state: FSMContext):
    """Хэндлер выбора количества вопросов в обычном тестировании"""
    user_id = message.from_user.id
    await load_check(user_id)
    try:
        q_amount = int(message.text)
        if q_amount < 1:
            raise ValueError("Количество вопросов должно быть положительным числом.")

        users[user_id].start_basic_test(q_amount=q_amount)
        await users[user_id].test.initialize_questions()
        await state.set_state(UserState.basic_test)
        await ask_question(message, user_id)

    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.")


async def ask_question(message: Message, user_id):
    """Функция достающая следующий вопрос из обычного теста"""
    question = await users[user_id].get_next_question()
    await message.answer(question, parse_mode=None)


@router.message(UserState.basic_test)
async def process_answer(message: Message):
    """Хэндлер обрабатывающий ответ на обычный тест"""
    user_id = message.from_user.id
    keyboard = kb.inline.next_q_or_feedback_kb if not users[user_id].test_completed() \
        else kb.inline.end_or_feedback_kb

    await message.reply(users[user_id].answer_question(message.text), reply_markup=keyboard)


@router.callback_query(lambda callback_query: callback_query.data in ['feedback', 'next_q', 'end_test'])
async def user_choice_test(callback_query: CallbackQuery, state: FSMContext):
    """Хэндлер фидбэка или получения следующего вопроса"""
    user_id = callback_query.from_user.id
    command = callback_query.data
    await callback_query.message.edit_reply_markup(reply_markup=None)
    if command == 'feedback':
        keyboard = kb.inline.next_q_kb if not users[user_id].test_completed() \
            else kb.inline.end_test_kb
        await callback_query.message.answer(users[user_id].test.give_feedback(), reply_markup=keyboard,
                                            parse_mode=None)

    elif command == 'next_q':
        await ask_question(callback_query.message, user_id)

    elif command == 'end_test':
        await callback_query.message.answer(users[user_id].test.test_result())
        await state.clear()
        await save_user_data(users[user_id])


async def ask_question_blitz(message: Message, user_id):
    """Функция достающая следующий вопрос из обычного теста"""
    question = await users[user_id].get_next_question()
    answers = question[1]

    buttons = list((value, key) for key, value in answers.items())
    random.shuffle(buttons)
    keyboard = kb.inline.create_inline_kb(tuple(buttons), row_width=1)

    await message.edit_text(question[0], reply_markup=keyboard)


@router.message(UserState.blitz_test)
@router.callback_query(lambda callback_query: callback_query.data in ['answer1', 'answer2', 'answer3', 'answer4'])
async def process_answer_blitz(callback_query: CallbackQuery):
    """Хэндлер обрабатывающий ответ на блиц тест"""
    user_id = callback_query.from_user.id
    answer = callback_query.data

    if answer == 'answer1':
        users[user_id].test.test_score += 1
    else:
        users[user_id].test.test_score -= 1

    if users[user_id].test_completed():
        if users[user_id].test.test_score > users[user_id].user_data['history']['blitz_record']:
            users[user_id].user_data['history']['blitz_record'] = users[user_id].test.test_score
            await save_user_data(users[user_id])

            await callback_query.message.edit_text('Личный рекорд!\n\n' + users[user_id].test.test_result())
        else:
            await callback_query.message.edit_text(users[user_id].test.test_result())
    else:
        await ask_question_blitz(callback_query.message, user_id)
