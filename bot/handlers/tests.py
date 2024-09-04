import random
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from bot.funcs.vars import users
from bot.funcs.bot_funcs import load_check
import bot.keyboards as kb
from bot.handlers.user_state import UserState

# роутер для передачи хэндлеров в основной скрипт
router = Router()


@router.callback_query(lambda callback_query: callback_query.data == 'test')
async def start_test(callback_query: CallbackQuery):
    """
    Хэндлер команды callback_query test
    """
    await callback_query.message.edit_text("Выбери режим", reply_markup=kb.inline.test_choice_kb)


@router.callback_query(lambda callback_query: callback_query.data in ['blitz_test', 'basic_test', 'mistakes'])
async def set_test_type(callback_query: CallbackQuery, state: FSMContext):
    """
    Хэндлер выбора варианта тестирования
    """
    user_id = callback_query.from_user.id
    await load_check(user_id)
    await callback_query.message.edit_reply_markup(reply_markup=None)
    test_type = callback_query.data

    if test_type == 'blitz_test':
        users[user_id].start_blitz_test()
        await state.set_state(UserState.blitz_test)
        await ask_question_blitz(callback_query.message, user_id)

    elif test_type == 'basic_test':
        await users[user_id].start_basic_test()
        await state.set_state(UserState.basic_test)
        await ask_question(callback_query.message, user_id)

    elif test_type == 'mistakes':
        await users[user_id].start_mistake_test()
        await state.set_state(UserState.basic_test)
        await ask_question(callback_query.message, user_id)


async def ask_question(message: Message, user_id):
    """
    Функция достающая следующий вопрос из обычного теста
    """
    question = await users[user_id].get_next_question()
    if not question:
        await message.edit_text("База ошибок пуста, поздравляю",
                                reply_markup=kb.inline.to_menu_kb)
    else:
        await message.answer(question, parse_mode=None)


@router.message(UserState.basic_test)
async def process_answer(message: Message):
    """
    Хэндлер обрабатывающий ответ на обычный тест / работу над ошибками
    """
    user_id = message.from_user.id
    await message.reply(await users[user_id].answer_question(message.text), reply_markup=kb.inline.test_kb)


@router.callback_query(lambda callback_query: callback_query.data in ['feedback', 'next_q'])
async def user_choice_test(callback_query: CallbackQuery):
    """
    Хэндлер фидбэка или получения следующего вопроса
    """
    user_id = callback_query.from_user.id
    command = callback_query.data
    await callback_query.message.edit_reply_markup(reply_markup=None)
    if command == 'feedback':
        try:
            await callback_query.message.edit_text(await users[user_id].test.give_feedback(),
                                                   reply_markup=kb.inline.feedback_kb)
        except TelegramBadRequest:
            await callback_query.message.edit_text(await users[user_id].test.give_feedback(),
                                                   reply_markup=kb.inline.feedback_kb,
                                                   parse_mode=None)

    elif command == 'next_q':
        await ask_question(callback_query.message, user_id)


async def ask_question_blitz(message: Message, user_id):
    """
    Функция достающая следующий вопрос из блиц теста
    """
    question = await users[user_id].get_next_question()
    answers = question[1]

    buttons = list((value, key) for key, value in answers.items())
    random.shuffle(buttons)
    keyboard = kb.inline.create_inline_kb(tuple(buttons), row_width=1)

    await message.edit_text(question[0], reply_markup=keyboard)


@router.callback_query(lambda callback_query: callback_query.data in ['answer1', 'answer2', 'answer3', 'answer4'])
async def process_answer_blitz(callback_query: CallbackQuery, state: FSMContext):
    """
    Хэндлер обрабатывающий ответ на блиц тест
    """
    user_id = callback_query.from_user.id
    answer = callback_query.data

    if answer == 'answer1':
        users[user_id].test.test_score += 1
        await users[user_id].get_blitz_exp()
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
        lvl_up = await users[user_id].level_up_check()
        if lvl_up:
            await callback_query.answer(lvl_up, show_alert=True)
    else:
        await ask_question_blitz(callback_query.message, user_id)
