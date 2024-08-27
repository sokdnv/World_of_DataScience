import json
import os
from bot.classes.user import User
from bot.funcs.vars import users
from bot.funcs.vars import user_info_blank


# TODO Переделать под доставание из базы данных
def load_user_data(file_path: str) -> dict:
    """
    Функция по загрузке json файла пользователя
    Если не находит такого - создает новый пустой
    """
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return user_info_blank


# TODO Переделать под закидывание в базу данных
def save_user_data(user: User) -> None:
    """Функция для сохранения данных о пользователе в json"""
    path = f'../data/users/{user.user_id}.json'
    with open(path, 'w') as file:
        json.dump(user.user_info, file, indent=4)


def load_user(user_id: int) -> User:
    # TODO Переделать под доставание из базы данных
    """ Функция создающая экземпляр класса Пользователь"""
    path = f'../data/users/{user_id}.json'
    user_data = load_user_data(path)
    user = User(user_id=user_id, info_json=user_data)
    return user


def load_check(user_id: int) -> None:
    # TODO Переделать под доставание из базы данных
    """Функция для загрузки юзера в кэш"""
    if not users.get(user_id):
        users[user_id] = load_user(user_id)
