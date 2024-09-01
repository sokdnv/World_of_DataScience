from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from bot.funcs.bot_funcs import load_check
import bot.classes.character_choice as cc
from bot.texts.greeting import greeting
from bot.keyboards.inline import greeting_kb
from bot.handlers.user_state import UserState
from bot.funcs.vars import users

router = Router()


@router.message(Command('start'))
async def send_welcome(message: Message):
    """Хэндлер команды /start"""
    user_id = message.from_user.id
    user_name = (message.from_user.first_name or "") + " " + (message.from_user.last_name or "").strip()
    await load_check(user_id, user_name)
    await message.answer(greeting(user_name), reply_markup=greeting_kb)


@router.callback_query(lambda callback_query: callback_query.data == 'char_name')
async def enter_character_name(callback_query: CallbackQuery, state: FSMContext):
    """Хэндлер для кнопки 'Ввести имя персонажа'"""
    await callback_query.message.edit_reply_markup(reply_markup=None)
    await callback_query.message.answer(
        "Имя должно состоять *минимум из 3 символов* и может содержать в себе *буквы и цифры*"
    )
    await state.set_state(UserState.character_name)


@router.message(UserState.character_name)
async def check_character_name(message: Message, state: FSMContext):
    """Функция проверки имени персонажа"""
    character_name = message.text

    if character_name.isalnum() and len(character_name) >= 3:
        await state.update_data(character_name=character_name)
        await state.set_state(UserState.character_race)
        await choose_character(message)
    else:
        await message.answer(
            "Введите корректное имя."
        )


@router.message(UserState.character_race)
async def choose_character(message: Message):
    """Хэндлер команды выбора персонажа"""
    user_id = message.from_user.id
    await load_check(user_id)

    photo = FSInputFile(cc.choice_file)
    await message.answer_photo(photo, reply_markup=cc.paginator(show_finish=False))


@router.callback_query(cc.CharacterChoice.filter(F.action.in_(('cat', 'dog', 'owl', 'finish'))))
async def character_choice(call: CallbackQuery, callback_data: cc.CharacterChoice, state: FSMContext):
    """Функция выбора персонажа"""
    action = callback_data.action
    user_id = call.from_user.id

    type_map = {
        'cat': 0,
        'dog': 1,
        'owl': 2,
    }

    if action in type_map:
        page = type_map[action]
        data = await state.get_data()
        if data.get("character_race") == action:
            await call.answer()
            return
        photo = FSInputFile(cc.choices[page])
        await call.message.delete()
        await call.message.answer_photo(photo, reply_markup=cc.paginator(page, show_finish=True))
        await state.update_data(character_race=action)
        callback_data.page = page

    elif action == 'finish':
        await call.message.edit_reply_markup(reply_markup=None)
        data = await state.get_data()
        await users[user_id].set_character(nickname=data["character_name"], character=data["character_race"])
        await call.message.answer(f'Персонаж *{data["character_race"].capitalize()}*'
                                  f' *{data["character_name"]}* создан!')
        await state.clear()

    await call.answer()
