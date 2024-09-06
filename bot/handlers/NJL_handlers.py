from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from bot.funcs.vars import users
from bot.funcs.bot_funcs import load_check
import bot.keyboards.inline as kb_i
from bot.handlers.user_state import UserState
from bot.funcs.database import top_blitz, top_players

# роутер для передачи хэндлеров в основной скрипт
router = Router()

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
