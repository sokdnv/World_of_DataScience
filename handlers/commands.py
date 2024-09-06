from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from funcs.vars import users
from funcs.load_funcs import load_check
import keyboards.inline as kb_i
from funcs.database import top_blitz, top_players

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
    await callback_query.message.answer_photo(await users[user_id].character_card(), reply_markup=kb_i.to_menu_kb)


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
                await message.edit_text(text=text, reply_markup=kb_i.idle_kb)
            except TelegramBadRequest:
                await message.answer(text=text, reply_markup=kb_i.idle_kb)
        else:
            await callback_query.message.answer(text=text, reply_markup=kb_i.idle_kb)
    else:
        await callback_query.answer(text=text, reply_markup=kb_i.idle_kb)


in_progress = '```🛠️\nWork in progress```'


@router.callback_query(F.data == 'jobs')
async def alg_results(callback_query: CallbackQuery):
    await callback_query.message.edit_text(text=in_progress, reply_markup=kb_i.to_menu_kb)


@router.callback_query(F.data == 'news')
async def alg_results(callback_query: CallbackQuery):
    await callback_query.message.edit_text(text=in_progress, reply_markup=kb_i.to_menu_kb)


@router.callback_query(F.data == 'leaderboard')
async def alg_results(callback_query: CallbackQuery):
    """
    Хэндер колбэка 'leaderboard'
    """
    text = '```🏆\n Choose leaderboard```'
    await callback_query.message.edit_text(text=text, reply_markup=kb_i.leader_kb)


@router.callback_query(F.data == 'top_players')
async def alg_results(callback_query: CallbackQuery):
    """
    Вывод картинки с топ игроками
    """
    await callback_query.message.delete()
    image = await top_players()
    await callback_query.message.answer_photo(image, reply_markup=kb_i.to_menu_kb)


@router.callback_query(F.data == 'top_blitz')
async def alg_results(callback_query: CallbackQuery):
    """
    Вывод картинки с блиц рекордами
    """
    await callback_query.message.delete()
    image = await top_blitz()
    await callback_query.message.answer_photo(image, reply_markup=kb_i.to_menu_kb)
