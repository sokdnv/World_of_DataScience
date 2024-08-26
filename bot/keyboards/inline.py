from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_inline_kb(buttons: tuple) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for text, callback in buttons:
        builder.button(text=text, callback_data=callback)

    return builder.as_markup()


alg_inline_kb = create_inline_kb((('Я решил', 'done'), ('Не получается...', 'fail')))
