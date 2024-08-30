from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    """
    Класс для обработки состояний юзера
    """
    character_name = State()
    character_race = State()
    awaiting_question_amount = State()
    basic_test = State()
    blitz_test = State()
