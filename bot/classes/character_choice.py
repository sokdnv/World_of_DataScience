import os
from PIL import Image
import io
from aiogram.types import BufferedInputFile
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
        InlineKeyboardButton(text='🔴', callback_data=CharacterChoice(action='red', page=page).pack()),
        InlineKeyboardButton(text='🔵', callback_data=CharacterChoice(action='blue', page=page).pack()),
        InlineKeyboardButton(text='🟢', callback_data=CharacterChoice(action='green', page=page).pack())

    )
    if show_finish:
        builder.row(
            InlineKeyboardButton(text='Choose', callback_data=CharacterChoice(action='finish', page=page).pack()),
        )

    return builder.as_markup()


current_dir = os.path.dirname(os.path.abspath(__file__))


def generate_character_image(character: str) -> BufferedInputFile:
    """
    Функция для генерации картинки с персонажем
    """
    background = Image.new('RGBA', (1125, 1218), color=(30, 30, 30, 255))
    img_path = os.path.join(current_dir, f"../image_gen/{character}_1.png")
    image = Image.open(img_path).convert("RGBA").resize((900, 900))

    background.paste(image, (112, 159), image)

    image_buffer = io.BytesIO()
    background.save(image_buffer, format='PNG')
    image_buffer.seek(0)
    photo_bytes = image_buffer.read()

    return BufferedInputFile(file=photo_bytes, filename='choice')


# Main screen выбора персонажа
choice_file = os.path.join(current_dir, "../image_gen/choice.png")
