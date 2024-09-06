def greeting(name: str, first: bool) -> str:
    """
    Функция для первичного приветствия пользователя
    """
    text = f"""```Hello\nПривет, {name}! 🎉 Добро пожаловать в World of Data Science!\nТвое путешествие по миру Data Science начинается здесь. Создай персонажа, прокачивай навыки и готовься к реальным собеседованиям!\nНачнём? Жми "Enter your name" и вперёд к новым знаниям! 🚀\nP.S. С этого момента меню будет на английском.```"""

    not_first = f'```Hello\nТы уже создавал персонажа```'
    return not_first if not first else text
