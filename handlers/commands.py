from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from funcs.vars import users
from funcs.load_funcs import load_check
import keyboards.inline as kb_i
from funcs.database import top_blitz, top_players, get_post, get_job

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


@router.callback_query(F.data == 'leaderboard')
async def show_leaderboards(callback_query: CallbackQuery):
    """
    Хэндер колбэка 'leaderboard'
    """
    text = '```🏆\nChoose leaderboard```'
    await callback_query.message.edit_text(text=text, reply_markup=kb_i.leader_kb)


@router.callback_query(F.data.in_(['top_players', 'top_blitz']))
async def show_top_players(callback_query: CallbackQuery):
    """
    Вывод картинки с топ игроками
    """
    await callback_query.message.delete()
    if callback_query.data == 'top_players':
        image = await top_players()
    else:
        image = await top_blitz()
    await callback_query.message.answer_photo(image, reply_markup=kb_i.to_menu_kb)


@router.callback_query(F.data.in_(['posts', 'jobs']))
async def show_content(callback_query: CallbackQuery):
    """
    Функция для отображения контента (вакансии или новости).
    """
    user_id = callback_query.from_user.id
    await load_check(user_id)
    content_type = callback_query.data

    if content_type in ['jobs', 'reset_jobs']:
        data = await get_job(user_id)
        end_of_content_kb = kb_i.end_of_jobs_kb
    else:
        data = await get_post(user_id)
        end_of_content_kb = kb_i.end_of_posts_kb

    if data:
        await callback_query.message.edit_text(
            text=data[1],
            reply_markup=kb_i.create_inline_kb(
                (('Link', data[0]), ('Next', content_type), ('Main menu', 'main_menu'))
            )
        )
    else:
        text = "```The_end\nThat's all for today```"
        await callback_query.message.edit_text(text=text, reply_markup=end_of_content_kb)


@router.callback_query(F.data.in_(['reset_posts', 'reset_jobs']))
async def reset_content(callback_query: CallbackQuery):
    """
    Функция для сброса истории контента (вакансии или новости).
    """
    user_id = callback_query.from_user.id
    content_type = callback_query.data.split('_')[1]
    await users[user_id].clear_history(jobs=(content_type == 'jobs'))
    await show_content(callback_query)


@router.callback_query(F.data == 'resources')
async def show_materials(callback_query: CallbackQuery):
    """
    Хэндер колбэка 'resources'
    """
    user_id = callback_query.from_user.id
    await load_check(user_id)
    link, text = await users[user_id].get_resource()
    await callback_query.message.edit_text(text=text,
                                           reply_markup=kb_i.create_inline_kb(
                                               (('Link', link), ('Next', 'resources'), ('Main menu', 'main_menu'))
                                           ))


@router.callback_query(F.data == 'content')
async def show_content(callback_query: CallbackQuery):
    """
    Хэндер колбэка 'content'
    """
    text = '```📰️\nChoose content type              🤓```'
    await callback_query.message.edit_text(text=text, reply_markup=kb_i.content_kb)


@router.callback_query(F.data == 'credits')
async def show_credits(callback_query: CallbackQuery):
    """
    Хэндер колбэка 'content'
    """
    text = ("```Created_by\n"
            "👾 Sergey Kudinov @s_kudinov\n"
            "🕹️ Konstantin Polyakov @Polyakov_Konstantin\n\n"
            "Don't hesitate to contact if you have any questions or encountered any bugs!```")
    await callback_query.message.edit_text(text=text, reply_markup=kb_i.to_menu_kb)
