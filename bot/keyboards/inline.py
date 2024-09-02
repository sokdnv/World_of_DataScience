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

basic_test_length_kb = create_inline_kb((('5', '5'), ('10', '10'), ('15', '15'), ('20', '20')))

test_choice_kb = create_inline_kb((('Обычное', 'basic_test'), ('Блиц', 'blitz_test'),
                                   ('Работа над ошибками', 'mistakes'), ('Назад', 'main_menu')))

end_or_feedback_kb = create_inline_kb((('Завершить тест', 'end_test'), ('Фидбэк', 'feedback')))
next_q_or_feedback_kb = create_inline_kb((('Следующий вопрос', 'next_q'), ('Фидбэк', 'feedback')))
next_q_kb = create_inline_kb((('Следующий вопрос', 'next_q'),))
end_test_kb = create_inline_kb((('Завершить тест', 'end_test'),))

idle_kb = create_inline_kb((('Тестирование', 'test'), ('Алгоритмы', 'alg'),
                            ('Новости', 'news'), ('Вакансии', 'jobs'),
                            ('Персонаж', 'stats'), ('Зал славы', 'leaderboard')))

to_menu_kb = create_inline_kb((('Главное меню', 'main_menu'),))

mistake_kb = create_inline_kb((('Следующий вопрос', 'next_q'), ('Фидбэк', 'feedback'),
                               ('Главное меню', 'main_menu')))
