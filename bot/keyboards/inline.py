from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_inline_kb(buttons: tuple, row_width: int = 2) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for text, callback in buttons:
        builder.button(text=text, callback_data=callback)

    builder.adjust(row_width)

    return builder.as_markup()


alg_inline_kb = create_inline_kb((('Я решил', 'done'), ('Не получается...', 'fail'),
                                  ('Назад', 'main_menu')))
greeting_kb = create_inline_kb((('Ввести имя персонажа', 'char_name'),))

test_choice_kb = create_inline_kb((('Обычный', 'basic_test'), ('Блиц', 'blitz_test'),
                                   ('Работа над ошибками', 'mistakes'), ('Назад', 'main_menu')))

idle_kb = create_inline_kb((('Вопросы', 'test'), ('Алгоритмы', 'alg'),
                            ('Новости', 'news'), ('Вакансии', 'jobs'),
                            ('Персонаж', 'stats'), ('Зал славы', 'leaderboard')))

to_menu_kb = create_inline_kb((('Главное меню', 'main_menu'),))

test_kb = create_inline_kb((('Следующий вопрос', 'next_q'), ('Фидбэк', 'feedback'),
                            ('Главное меню', 'main_menu')))

feedback_kb = create_inline_kb((('Следующий вопрос', 'next_q'), ('Главное меню', 'main_menu')))
