from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

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

    await callback_query.message.edit_reply_markup(reply_markup=None)
    await callback_query.message.answer_photo(await users[user_id].character_card(), reply_markup=to_menu_kb)


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
    await callback_query.message.edit_reply_markup(reply_markup=None)

    last_message = callback_query.message
    if last_message.photo:
        await last_message.delete()

    user_id = callback_query.from_user.id
    await load_check(user_id)

    lvl_up = await users[user_id].level_up_check()
    if lvl_up:
        await callback_query.answer(lvl_up, show_alert=True)

    try:
        await callback_query.message.edit_text(text='*Главное меню*', reply_markup=idle_kb)
    except TelegramBadRequest:
        await callback_query.message.answer(text='*Главное меню*', reply_markup=idle_kb)

