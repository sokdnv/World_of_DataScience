import random
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.funcs.vars import users
from bot.funcs.bot_funcs import load_check
import bot.keyboards as kb
from bot.handlers.user_state import UserState

# роутер для передачи хэндлеров в основной скрипт
router = Router()


@router.callback_query(lambda callback_query: callback_query.data == 'test')
async def start_test(callback_query: CallbackQuery):
    """Хэндлер команды /test"""
    await callback_query.message.edit_text("Выбери тип тестирования", reply_markup=kb.inline.test_choice_kb)


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
        await callback_query.message.edit_text("На сколько вопросов вы хотите ответить?",
                                               reply_markup=kb.inline.basic_test_length_kb)


@router.callback_query(lambda callback_query: callback_query.data in ['5', '10', '15', '20'])
async def set_test_q_amount(callback_query: CallbackQuery, state: FSMContext):
    """Хэндлер выбора количества вопросов в обычном тестировании"""
    await callback_query.message.edit_reply_markup(reply_markup=None)
    user_id = callback_query.from_user.id
    await load_check(user_id)
    q_amount = int(callback_query.data)

    await users[user_id].start_basic_test(q_amount=q_amount)
    await users[user_id].test.initialize_questions()
    await state.set_state(UserState.basic_test)
    await ask_question(callback_query.message, user_id)


async def ask_question(message: Message, user_id):
    """Функция достающая следующий вопрос из обычного теста"""
    question = await users[user_id].get_next_question()
    await message.answer(question, parse_mode=None)


@router.message(UserState.basic_test)
async def process_answer(message: Message):
    """Хэндлер обрабатывающий ответ на обычный тест"""
    user_id = message.from_user.id
    keyboard = kb.inline.next_q_or_feedback_kb if not await users[user_id].test_completed() \
        else kb.inline.end_or_feedback_kb

    await message.reply(users[user_id].answer_question(message.text), reply_markup=keyboard)


@router.callback_query(lambda callback_query: callback_query.data in ['feedback', 'next_q', 'end_test'])
async def user_choice_test(callback_query: CallbackQuery, state: FSMContext):
    """Хэндлер фидбэка или получения следующего вопроса"""
    user_id = callback_query.from_user.id
    command = callback_query.data
    await callback_query.message.edit_reply_markup(reply_markup=None)
    if command == 'feedback':
        keyboard = kb.inline.next_q_kb if not await users[user_id].test_completed() \
            else kb.inline.end_test_kb
        await callback_query.message.answer(users[user_id].test.give_feedback(), reply_markup=keyboard,
                                            parse_mode=None)

    elif command == 'next_q':
        await ask_question(callback_query.message, user_id)

    elif command == 'end_test':
        await callback_query.message.answer(users[user_id].test.test_result(), reply_markup=kb.inline.to_menu_kb)
        await state.clear()


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
async def process_answer_blitz(callback_query: CallbackQuery, state: FSMContext):
    """Хэндлер обрабатывающий ответ на блиц тест"""
    user_id = callback_query.from_user.id
    answer = callback_query.data

    if answer == 'answer1':
        users[user_id].test.test_score += 1
    else:
        users[user_id].test.test_score -= 1

    if await users[user_id].test_completed():
        await state.clear()
        if users[user_id].test.test_score > await users[user_id].get_blitz_record():
            await users[user_id].set_blitz_record(users[user_id].test.test_score)

            await callback_query.message.edit_text('Личный рекорд!\n\n' + users[user_id].test.test_result(),
                                                   reply_markup=kb.inline.to_menu_kb)
        else:
            await callback_query.message.edit_text(users[user_id].test.test_result(),
                                                   reply_markup=kb.inline.to_menu_kb)
    else:
        await ask_question_blitz(callback_query.message, user_id)
