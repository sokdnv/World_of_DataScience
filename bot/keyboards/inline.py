from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_inline_kb(buttons: tuple, row_width: int = 2) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for text, callback in buttons:
        builder.button(text=text, callback_data=callback)

    builder.adjust(row_width)

    return builder.as_markup()


alg_inline_kb = create_inline_kb((('Я решил', 'done'), ('Не получается...', 'fail')))
greeting_kb = create_inline_kb((('Ввести имя персонажа', 'char_name'),))

test_choice_kb = create_inline_kb((('Обычное', 'basic_test'), ('Блиц', 'blitz_test')), )
end_or_feedback_kb = create_inline_kb((('Завершить тест', 'end_test'), ('Фидбэк', 'feedback')))
next_q_or_feedback_kb = create_inline_kb((('Следующий вопрос', 'next_q'), ('Фидбэк', 'feedback')))
next_q_kb = create_inline_kb((('Следующий вопрос', 'next_q'),))
end_test_kb = create_inline_kb((('Завершить тест', 'end_test'),))
