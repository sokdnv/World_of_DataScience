from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.funcs.vars import users
from bot.funcs.bot_funcs import load_check
from bot.keyboards.inline import to_menu_kb, idle_kb

# роутер для передачи хэндлеров в основной скрипт
router = Router()


@router.callback_query(lambda callback_query: callback_query.data == 'stats')
async def show_stats(callback_query: CallbackQuery):
    """
    Хэндлер callback_query stats
    """
    user_id = callback_query.from_user.id
    await load_check(user_id)
    await callback_query.message.edit_text(await users[user_id].stats(), reply_markup=to_menu_kb)


@router.message(Command('clear'))
async def clear_user_info(message: Message):
    """
    Хэндлер команды /clear
    """
    user_id = message.from_user.id
    await load_check(user_id)

    await users[user_id].clear_data()
    await message.answer("Статистика удалена")


@router.callback_query(lambda callback_query: callback_query.data == 'main_menu')
async def main_menu(callback_query: CallbackQuery, state: FSMContext):
    """
    Хэндлер вызова основного меню
    """
    await state.clear()
    user_id = callback_query.from_user.id
    await load_check(user_id)
    await callback_query.message.edit_text(text='*Главное меню*', reply_markup=idle_kb)
