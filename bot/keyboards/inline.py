from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_inline_kb(buttons: tuple, row_width: int = 2) -> InlineKeyboardMarkup:
    """
    Функция для создания inline клавиатур
    """
    builder = InlineKeyboardBuilder()

    for text, callback in buttons:
        builder.button(text=text, callback_data=callback)

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

tutorial_kb_1 = create_inline_kb((('Got it!', 'part_1'),))
tutorial_kb_2 = create_inline_kb((('Okay!', 'part_2'),))
tutorial_kb_3 = create_inline_kb((('Cool!', 'part_3'),))
tutorial_kb_4 = create_inline_kb((('Amazing!', 'part_4'),))
tutorial_kb_5 = create_inline_kb((("Let's go!", 'main_menu'),))
