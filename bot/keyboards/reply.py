from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from typing import List, Optional


def create_reply_keyboard(
    buttons: List[List[str]],
    resize_keyboard: bool = True,
    one_time_keyboard: bool = True,
    placeholder: Optional[str] = None
) -> ReplyKeyboardMarkup:
    """
    Функция для создания клавиатуры.
    """
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=text) for text in row] for row in buttons],
        resize_keyboard=resize_keyboard,
        one_time_keyboard=one_time_keyboard,
        input_field_placeholder=placeholder
    )


test_choice_kb = create_reply_keyboard([['Обычное', 'Блиц']])
end_or_feedback_kb = create_reply_keyboard([['Завершить тест', 'Фидбэк']])
next_q_or_feedback_kb = create_reply_keyboard([['Следующий вопрос', 'Фидбэк']])
next_q_kb = create_reply_keyboard([['Следующий вопрос']])
end_test_kb = create_reply_keyboard([['Завершить тест']])
