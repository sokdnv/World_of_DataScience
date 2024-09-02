from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.funcs.vars import users
from bot.funcs.bot_funcs import load_check
import bot.keyboards.inline as kb_i

# роутер для передачи хэндлеров в основной скрипт
router = Router()


@router.callback_query(lambda callback_query: callback_query.data == 'alg')
async def give_alg_task(callback_query: CallbackQuery):
    """Хэндлер команды /alg"""
    user_id = callback_query.from_user.id
    await load_check(user_id)

    await users[user_id].get_algo_task()
    await callback_query.message.edit_text(users[user_id].test.get_task_text(),
                                           reply_markup=kb_i.alg_inline_kb)


@router.callback_query(F.data.in_(['done', 'fail']))
async def alg_results(call: CallbackQuery):
    user_id = call.from_user.id
    callback_data = call.data
    if callback_data == 'done':
        new_text = 'Молодец!'
        fail = False
    else:
        new_text = f'[Решение]({users[user_id].test.get_task_solution()})'
        fail = True

    await users[user_id].algo_task_solved(fail=fail)
    await call.message.edit_text(new_text, reply_markup=kb_i.to_menu_kb)
    await call.answer()
