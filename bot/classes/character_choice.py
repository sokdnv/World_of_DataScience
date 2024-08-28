import os
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup


class CharacterChoice(CallbackData, prefix='ch'):
    """Класс для отображения информации при выборе персонажа"""
    action: str
    page: int


def paginator(page: int = 0, show_finish: bool = False) -> InlineKeyboardMarkup:
    """Функция, создающая inline клавиатуру при выборе персонажа"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='🐱', callback_data=CharacterChoice(action='cat', page=page).pack()),
        InlineKeyboardButton(text='🐶', callback_data=CharacterChoice(action='dog', page=page).pack()),
        InlineKeyboardButton(text='🦉', callback_data=CharacterChoice(action='owl', page=page).pack())

    )
    if show_finish:
        builder.row(
            InlineKeyboardButton(text='Сделать выбор', callback_data=CharacterChoice(action='finish', page=page).pack()),
        )

    return builder.as_markup()


current_dir = os.path.dirname(os.path.abspath(__file__))

# картинки с классами
choices = [
    os.path.join(current_dir, "../../data/images/cat.png"),
    os.path.join(current_dir, "../../data/images/dog.png"),
    os.path.join(current_dir, "../../data/images/owl.png"),
]

# Main screen выбора персонажа
choice_file = os.path.join(current_dir, "../../data/images/choice.png")
