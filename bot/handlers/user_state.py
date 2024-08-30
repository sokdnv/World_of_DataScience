from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    """
    Класс для обработки состояний юзера
    """
    character_name = State()
    character_race = State()
    awaiting_question_amount = State()
    answering = State()
    feedback = State()
