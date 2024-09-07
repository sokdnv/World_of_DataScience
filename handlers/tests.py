import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from funcs.vars import users
from funcs.load_funcs import load_check
from handlers.user_state import UserState
import keyboards.inline as kb_i

# роутер для передачи хэндлеров в основной скрипт
router = Router()


@router.callback_query(F.data == 'test')
async def start_test(callback_query: CallbackQuery):
    """
    Хэндлер команды callback_query test
    """
    await callback_query.message.edit_text("```Questions\nChoose play mode```", reply_markup=kb_i.test_choice_kb)


@router.callback_query(F.data.in_(['blitz_test', 'basic_test', 'mistakes']))
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
        await ask_question_blitz(callback_query)

    elif test_type == 'basic_test':
        await users[user_id].start_basic_test()
        await state.set_state(UserState.basic_test)
        await ask_question(callback_query, state)

    elif test_type == 'mistakes':
        await users[user_id].start_mistake_test()
        await state.set_state(UserState.basic_test)
        await ask_question(callback_query, state)


async def ask_question(callback_query: CallbackQuery, state: FSMContext):
    """
    Функция достающая следующий вопрос из обычного теста
    """
    user_id = callback_query.from_user.id
    question = await users[user_id].get_next_question()
    if not question:
        if users[user_id].test.get_name() == 'BasicTest':
            text = '```🙃\nNo more questions for your level.\nDo another leveling activity```'
        else:
            text = '```🎉\nMistake pool is empty```'
        await callback_query.message.edit_text(text=text,
                                               reply_markup=kb_i.to_menu_kb)
    else:
        await callback_query.message.edit_text(text=question,
                                               reply_markup=kb_i.dont_know_kb)
        await state.update_data(message_id=callback_query.message.message_id)


@router.message(UserState.basic_test)
@router.callback_query(F.data == 'pass')
async def process_answer(message: Message | CallbackQuery, state: FSMContext):
    """
    Хэндлер обрабатывающий ответ на обычный тест / работу над ошибками
    """
    user_id = message.from_user.id
    if isinstance(message, CallbackQuery):
        await users[user_id].answer_question(skip=True)
        await ask_question(message, state)
    else:
        data = await state.get_data()
        await message.bot.edit_message_reply_markup(chat_id=user_id,
                                                    message_id=data['message_id'],
                                                    reply_markup=None)
        score = await users[user_id].answer_question(message.text)
        await message.answer(text=f'```score\n{score}```', reply_markup=kb_i.test_kb)


@router.callback_query(F.data.in_(['feedback', 'next_q']))
async def user_choice_test(callback_query: CallbackQuery, state: FSMContext):
    """
    Хэндлер фидбэка или получения следующего вопроса
    """
    user_id = callback_query.from_user.id
    command = callback_query.data
    await callback_query.message.edit_reply_markup(reply_markup=None)
    if command == 'feedback':
        try:
            await callback_query.message.edit_text(await users[user_id].test.give_feedback(),
                                                   reply_markup=kb_i.feedback_kb)
        except TelegramBadRequest:
            await callback_query.message.edit_text(await users[user_id].test.give_feedback(),
                                                   reply_markup=kb_i.feedback_kb,
                                                   parse_mode=None)

    elif command == 'next_q':
        await ask_question(callback_query, state)


async def ask_question_blitz(callback_query: CallbackQuery):
    """
    Функция достающая следующий вопрос из блиц теста
    """
    user_id = callback_query.from_user.id
    question = await users[user_id].get_next_question()
    answers = question[1]

    buttons = list((value, key) for key, value in answers.items())
    random.shuffle(buttons)
    keyboard = kb_i.create_inline_kb(tuple(buttons), row_width=1)

    await callback_query.message.edit_text(question[0], reply_markup=keyboard)


@router.callback_query(F.data.in_(['answer1', 'answer2', 'answer3', 'answer4']))
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

            await callback_query.message.edit_text('🎉Personal record!🎉\n\n' + users[user_id].test.test_result(),
                                                   reply_markup=kb_i.to_menu_kb)
        else:
            await callback_query.message.edit_text(users[user_id].test.test_result(),
                                                   reply_markup=kb_i.to_menu_kb)
        lvl_up = await users[user_id].level_up_check()
        if lvl_up:
            await callback_query.answer(lvl_up, show_alert=True)
    else:
        await ask_question_blitz(callback_query)
