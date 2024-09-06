from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_inline_kb(buttons: tuple, row_width: int = 2) -> InlineKeyboardMarkup:
    """
    Функция для создания inline клавиатур
    """
    builder = InlineKeyboardBuilder()

    for text, action in buttons:
        if action.startswith('http'):
            builder.button(text=text, url=action)
        else:
            builder.button(text=text, callback_data=action)

    builder.adjust(row_width)
    return builder.as_markup()


alg_inline_kb = create_inline_kb((('Done', 'done'), ("I'm stuck", "fail"),
                                  ('🔙Back', 'main_menu')))

greeting_kb = create_inline_kb((('Enter your name', 'char_name'),))

test_choice_kb = create_inline_kb((('Basic', 'basic_test'), ('Blitz', 'blitz_test'),
                                   ('Mistakes', 'mistakes'), ('🔙Back', 'main_menu')))

idle_kb = create_inline_kb((('Questions', 'test'), ('Algorithms', 'alg'),
                            ('News', 'news'), ('Jobs', 'jobs'),
                            ('Character', 'stats'), ('Leaderboards', 'leaderboard')))

to_menu_kb = create_inline_kb((('Main menu', 'main_menu'),))

test_kb = create_inline_kb((('Another question', 'next_q'), ('Feedback', 'feedback'),
                            ('Main menu', 'main_menu')))

feedback_kb = create_inline_kb((('Another question', 'next_q'), ('Main menu', 'main_menu')))

feedback_alg_kb = create_inline_kb((('Main menu', 'main_menu'), ('Feedback', 'feedback_alg')))

dont_know_kb = create_inline_kb((("Don't know", 'pass'), ('Main menu', 'main_menu'),))

enter_world_kb = create_inline_kb((('Enter the World of Data Science', 'enter'),))

leader_kb = create_inline_kb((('Top players', 'top_players'), ('Blitz records', 'top_blitz'),
                              ('🔙Back', 'main_menu')))
