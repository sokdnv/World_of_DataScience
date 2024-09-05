from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from bot.funcs.vars import users
from bot.funcs.bot_funcs import load_check
from bot.keyboards.inline import to_menu_kb, idle_kb

# роутер для передачи хэндлеров в основной скрипт
router = Router()


@router.callback_query(F.data == 'stats')
async def show_stats(callback_query: CallbackQuery):
    """
    Хэндлер callback_query stats
    """
    user_id = callback_query.from_user.id
    await load_check(user_id)

    await callback_query.message.delete()
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


@router.callback_query(F.data == 'main_menu')
@router.message(Command('menu'))
async def main_menu(callback_query: CallbackQuery | Message, state: FSMContext):
    """
    Хэндлер вызова основного меню
    """
    await state.clear()
    user_id = callback_query.from_user.id
    await load_check(user_id)

    lvl_up = await users[user_id].level_up_check()
    if lvl_up:
        await callback_query.answer(lvl_up, show_alert=True)

    text = '```Data_rpg\nMain menu```'

    if isinstance(callback_query, CallbackQuery):
        message = callback_query.message
        if message:
            if message.photo:
                await message.delete()
            try:
                await message.edit_text(text=text, reply_markup=idle_kb)
            except TelegramBadRequest:
                await message.answer(text=text, reply_markup=idle_kb)
        else:
            await callback_query.message.answer(text=text, reply_markup=idle_kb)
    else:
        await callback_query.answer(text=text, reply_markup=idle_kb)