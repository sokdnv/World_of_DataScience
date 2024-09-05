from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from bot.funcs.bot_funcs import load_check
import bot.classes.character_choice as cc
from bot.texts.greeting import greeting
from bot.keyboards.inline import greeting_kb, idle_kb, to_menu_kb
from bot.handlers.user_state import UserState
from bot.funcs.vars import users

router = Router()


@router.message(Command('start'))
async def send_welcome(message: Message):
    """
    Хэндлер команды /start
    """
    user_id = message.from_user.id
    user_name = (message.from_user.first_name or "") + " " + (message.from_user.last_name or "").strip()
    await load_check(user_id, user_name)
    check = await users[user_id].get_nickname()
    await message.answer(greeting(user_name, first=not check), reply_markup=to_menu_kb if check else greeting_kb)


@router.callback_query(F.data == 'char_name')
async def enter_character_name(callback_query: CallbackQuery, state: FSMContext):
    """
    Хэндлер для кнопки 'Ввести имя персонажа'
    """
    await callback_query.message.edit_reply_markup(reply_markup=None)
    await callback_query.message.answer(
        "```Reminder\n"
        "The name must be between 3 to 12 characters long and can contain letters and numbers."
        "```"
    )
    await state.set_state(UserState.character_name)


@router.message(UserState.character_name)
async def check_character_name(message: Message, state: FSMContext):
    """
    Функция проверки имени персонажа
    """
    character_name = message.text

    if character_name.isalnum() and 3 <= len(character_name) <= 12:
        await state.update_data(character_name=character_name)
        await state.set_state(UserState.character_race)
        await choose_character(message)
    else:
        await message.answer(
            "```Error\n"
            "Enter correct name"
            "```"
        )


@router.message(UserState.character_race)
async def choose_character(message: Message):
    """
    Хэндлер команды выбора персонажа
    """
    user_id = message.from_user.id
    await load_check(user_id)

    photo = FSInputFile(cc.choice_file)
    await message.answer_photo(photo, reply_markup=cc.paginator(show_finish=False))


@router.callback_query(cc.CharacterChoice.filter(F.action.in_(('red', 'blue', 'green', 'finish'))))
async def character_choice(call: CallbackQuery, callback_data: cc.CharacterChoice, state: FSMContext):
    """
    Функция выбора персонажа
    """
    action = callback_data.action
    user_id = call.from_user.id

    type_map = {
        'red': 0,
        'blue': 1,
        'green': 2,
    }

    if action in type_map:
        page = type_map[action]
        data = await state.get_data()
        if data.get("character_race") == action:
            await call.answer()
            return
        photo = cc.generate_character_image(character=action)
        await call.message.delete()
        await call.message.answer_photo(photo, reply_markup=cc.paginator(page, show_finish=True))
        await state.update_data(character_race=action)
        callback_data.page = page

    elif action == 'finish':
        await call.message.edit_reply_markup(reply_markup=None)
        data = await state.get_data()
        await users[user_id].set_character(nickname=data["character_name"], character=data["character_race"])
        await call.message.answer(f'```🎉\n'
                                  f'Student {data["character_name"]} was created!```')
        await idle(call, state)

    await call.answer()


@router.message(Command('menu'))
async def idle(callback_query: CallbackQuery | Message, state: FSMContext):
    """
    Вызов главного меню после выбора персонажа
    """
    await state.clear()
    user_id = callback_query.from_user.id
    await load_check(user_id)
    text = '```Data_rpg\nMain menu```'

    if isinstance(callback_query, CallbackQuery):
        if callback_query.message:
            try:
                await callback_query.message.edit_reply_markup(reply_markup=None)
            except TelegramBadRequest:
                pass
            await callback_query.message.answer(text=text, reply_markup=idle_kb)
        else:
            await callback_query.answer(text=text, reply_markup=idle_kb)
    else:
        await callback_query.answer(text=text, reply_markup=idle_kb)

