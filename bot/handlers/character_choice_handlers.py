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

    await message.answer('Выбери персонажа', reply_markup=cc.paginator(show_finish=False))


@router.callback_query(cc.CharacterChoice.filter(F.action.in_(('cat', 'dog', 'owl', 'finish'))))
async def character_choice(call: CallbackQuery, callback_data: cc.CharacterChoice):
    global last_selected
    action = callback_data.action

    type_map = {
        'cat': (0, "Вы выбрали котика!"),
        'dog': (1, "Вы выбрали собачку!"),
        'owl': (2, "Вы выбрали сову!")
    }

    if action in type_map:
        page = type_map[action][0]
        photo = FSInputFile(cc.choices[page])
        last_selected = action
        await call.message.delete()
        await call.message.answer_photo(photo, reply_markup=cc.paginator(page, show_finish=True))
    elif action == 'finish':
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer(type_map[last_selected][1])
        del last_selected

    await call.answer()
