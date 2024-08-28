from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.funcs.bot_funcs import save_user_data
from bot.funcs.vars import users
from bot.funcs.bot_funcs import load_check

# роутер для передачи хэндлеров в основной скрипт
router = Router()


@router.message(Command('start'))
async def send_welcome(message: Message):
    """Хэндлер команды /start"""
    user_id = message.from_user.id
    user_name = (message.from_user.first_name or "") + " " + (message.from_user.last_name or "").strip()
    await load_check(user_id, user_name)

    await message.answer(f"Привет *{message.from_user.first_name}*! Я бот для тестирования твоих знаний\n"
                         f"Ты можешь начать тест с помощью команды /test")


@router.message(Command('stats'))
async def show_stats(message: Message):
    """Хэндлер команды /stats"""
    user_id = message.from_user.id
    await load_check(user_id)

    await message.answer(users[user_id].stats())


@router.message(Command('clear'))
async def clear_user_info(message: Message):
    """Хэндлер команды /clear"""
    user_id = message.from_user.id
    await load_check(user_id)

    await users[user_id].clear_data()
    await save_user_data(users[user_id])
    await message.answer("Статистика удалена")
