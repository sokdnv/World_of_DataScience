from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from bot.funcs.bot_funcs import save_user_data
from bot.funcs.vars import users
from bot.funcs.bot_funcs import load_check
import bot.keyboards.reply as kb_r
import bot.keyboards.inline as kb_i


# роутер для передачи хэндлеров в основной скрипт
router = Router()


@router.message(Command('alg'))
async def give_alg_task(message: Message):
    """Хэндлер команды /alg"""
    user_id = message.from_user.id
    load_check(user_id)

    users[user_id].get_algo_task()
    await message.answer(users[user_id].test.get_task_text(),
                         reply_markup=kb_i.alg_inline_kb)


@router.callback_query(F.data.in_(['done', 'fail']))
async def alg_results(call: CallbackQuery):
    user_id = call.from_user.id
    callback_data = call.data
    if callback_data == 'done':
        new_text = 'Молодец!'
    else:
        new_text = f'[Решение]({users[user_id].test.get_task_solution()})'

    await call.message.edit_text(new_text)
    await call.answer()
