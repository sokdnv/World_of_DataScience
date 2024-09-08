from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from funcs.load_funcs import load_check
import classes.character_choice as cc
from texts.greeting import greeting
import keyboards.inline as kb_i
from handlers.user_state import UserState
from funcs.vars import users
import texts.tutorial as tut
from funcs.database import get_nicknames

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
    await message.answer(greeting(user_name, first=not check),
                         reply_markup=kb_i.to_menu_kb if check else kb_i.greeting_kb)


@router.callback_query(F.data == 'char_name')
async def enter_character_name(callback_query: CallbackQuery, state: FSMContext):
    """
    Хэндлер для кнопки 'Ввести имя персонажа'
    """
    await callback_query.message.edit_reply_markup(reply_markup=None)
    response = await callback_query.message.answer(
        "```Reminder\n"
        "The name must be between 3 to 12 characters long and can contain english letters and numbers."
        "```"
    )
    await state.set_state(UserState.character_name)
    await state.update_data(message_id=response.message_id)


@router.message(UserState.character_name)
async def check_character_name(message: Message, state: FSMContext):
    """
    Функция проверки имени персонажа
    """
    character_name = message.text

    if character_name in await get_nicknames():
        await message.answer(
            "```Error\n"
            "Name already taken"
            "```"
        )
    elif character_name.isalnum() and character_name.isascii() and 3 <= len(character_name) <= 12:
        await state.update_data(character_name=character_name)
        await state.set_state(UserState.character_race)
        data = await state.get_data()
        await message.bot.delete_message(chat_id=message.from_user.id, message_id=data['message_id'])
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

    photo = await cc.choice_file()
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
        photo = await cc.generate_character_image(character=action)
        await call.message.delete()
        await call.message.answer_photo(photo, reply_markup=cc.paginator(page, show_finish=True))
        await state.update_data(character_race=action)
        callback_data.page = page

    elif action == 'finish':
        await call.message.edit_reply_markup(reply_markup=None)
        data = await state.get_data()
        await users[user_id].set_character(nickname=data["character_name"], character=data["character_race"])
        await call.message.answer(f'```🎉\nStudent {data["character_name"]} was created!```',
                                  reply_markup=kb_i.enter_world_kb)

    await call.answer()


tutorial_steps = {
    'enter': (tut.part_1, 'part_1', 'Got it!'),
    'part_1': (tut.part_2, 'part_2', 'Okay!'),
    'part_2': (tut.part_3, 'part_3', 'Cool!'),
    'part_3': (tut.part_4, 'part_4', 'Amazing!'),
    'part_4': (tut.part_5, 'part_5', 'Awesome!'),
    'part_5': (tut.part_6, 'part_6', 'Wow!'),
    'part_6': (tut.part_7, 'part_7', 'Oh my god!'),
    'part_7': (tut.part_8, 'part_8', "Can't wait!"),
    'part_8': (tut.part_9, 'part_9', "Brilliant!"),
    'part_9': (tut.part_10, 'main_menu', "Let's go!!"),
}


@router.callback_query(F.data.in_(tutorial_steps.keys()))
async def tutorial_handler(callback_query: CallbackQuery):
    step_data = tutorial_steps[callback_query.data]

    text, next_step, button_text = step_data

    await callback_query.message.edit_text(
        text=text,
        reply_markup=kb_i.create_inline_kb(((button_text, next_step),))
    )

