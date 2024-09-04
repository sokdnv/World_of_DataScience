from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from bot.funcs.vars import users
from bot.funcs.bot_funcs import load_check
import bot.keyboards.inline as kb_i
from bot.handlers.user_state import UserState

# роутер для передачи хэндлеров в основной скрипт
router = Router()


@router.callback_query(lambda callback_query: callback_query.data == 'alg')
async def give_alg_task(callback_query: CallbackQuery):
    """
    Хэндлер callback alg
    """
    user_id = callback_query.from_user.id
    await load_check(user_id)

    await users[user_id].get_algo_task()
    await callback_query.message.edit_text(users[user_id].test.get_task_text(),
                                           reply_markup=kb_i.alg_inline_kb)


@router.callback_query(F.data.in_(['done', 'fail']))
async def alg_results(callback_query: CallbackQuery, state: FSMContext):
    """
    Хэндлер результатов решения алгоритмической задачи
    """
    user_id = callback_query.from_user.id
    callback_data = callback_query.data
    if callback_data == 'done':
        await state.set_state(UserState.algo_task)
        text = '```📜\nSend me your code```'
        await callback_query.message.edit_text(text=text,
                                               reply_markup=None)

    else:
        text = f'[Solution]({users[user_id].test.get_task_solution()})'
        await users[user_id].algo_task_solved(fail=True)
        await callback_query.message.edit_text(text=text, reply_markup=kb_i.to_menu_kb)
    await callback_query.answer()


@router.message(UserState.algo_task)
async def alg_results(message: Message, state: FSMContext):
    """
    Хэндлер для проверки кода задачки по алгоритмам
    """
    user_id = message.from_user.id
    code = message.text
    await state.clear()

    result = await users[user_id].test.check_algo_solution(code=code)
    if result.lower()[:7] == 'принято':
        await users[user_id].algo_task_solved(fail=False)
        text = '```✅\nAccepted```'
    else:
        text = '```❌\nDenied```'
    await message.answer(text=text, reply_markup=kb_i.feedback_alg_kb)


@router.callback_query(F.data == 'feedback_alg')
async def alg_results(callback_query: CallbackQuery):
    """
    Хэндлер для получения фидбэка по алгоритмической задаче
    """
    user_id = callback_query.from_user.id

    feedback = await users[user_id].test.check_algo_solution(feedback=True)
    try:
        await callback_query.message.edit_text(text=feedback, reply_markup=kb_i.to_menu_kb)
    except TelegramBadRequest:
        await callback_query.message.edit_text(text=feedback, reply_markup=kb_i.to_menu_kb, parse_mode=None)
