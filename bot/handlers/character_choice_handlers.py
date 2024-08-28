from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile

from bot.funcs.bot_funcs import load_check
import bot.classes.character_choice as cc

router = Router()


@router.message(Command('choice'))
async def choose_character(message: Message):
    """Хэндлер команды выбора персонажа"""
    user_id = message.from_user.id
    load_check(user_id)

    photo = FSInputFile(cc.choice_file)
    await message.answer_photo(photo, reply_markup=cc.paginator(show_finish=False))


@router.callback_query(cc.CharacterChoice.filter(F.action.in_(('cat', 'dog', 'owl', 'finish'))))
async def character_choice(call: CallbackQuery, callback_data: cc.CharacterChoice):
    """Функция выбора персонажа"""
    action = callback_data.action

    type_map = {
        'cat': (0, "Вы выбрали котика!"),
        'dog': (1, "Вы выбрали собачку!"),
        'owl': (2, "Вы выбрали сову!")
    }

    if action in type_map:
        page = type_map[action][0]
        photo = FSInputFile(cc.choices[page])
        await call.message.delete()
        await call.message.answer_photo(photo, reply_markup=cc.paginator(page, show_finish=True))
        callback_data.page = page

    elif action == 'finish':
        selected_message = [msg for (idx, msg) in type_map.values() if idx == callback_data.page][0]
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer(selected_message)

    await call.answer()

