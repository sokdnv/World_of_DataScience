from aiogram.types import (ReplyKeyboardMarkup,
                           KeyboardButton)

# клавиатура для выбора типа теста
test_type_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Обычное'),
            KeyboardButton(text='Блиц')
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выбери тип теста',
    one_time_keyboard=True
)

# клавиатура для запроса фидбэка от чатбота
feedback_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Следующий вопрос'),
            KeyboardButton(text='Фидбэк')
        ]
    ],
    one_time_keyboard=True
)

next_q_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Следующий вопрос')
        ]
    ],
    one_time_keyboard=True
)


final_q_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Завершить тест'),
            KeyboardButton(text='Фидбэк')
        ]
    ],
    one_time_keyboard=True
)

finish_test_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Завершить тест')
        ]
    ],
    one_time_keyboard=True
)
