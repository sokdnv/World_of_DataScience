from bot.classes.user import User
from bot.funcs.vars import users
from bot.funcs.database import user_collection, add_user_to_db


async def load_user_data(user_id: int, user_name: str) -> dict:
    """
    Загрузка информации о пользователе из базы данных
    """
    user_data = await user_collection.find_one({"_id": user_id})
    if not user_data:
        user_data = await add_user_to_db(user_id, user_name)
    return user_data


# async def save_user_data(user: User) -> None:
#     """
#     Сохранение информации о пользователе в базу данных
#     """
#     await user_collection.update_one({"_id": user.user_id}, {"$set": user.user_data})


async def load_user(user_id: int, user_name: str) -> User:
    """ Функция создающая экземпляр класса Пользователь"""
    await load_user_data(user_id, user_name)
    user = User(user_id=user_id)
    return user


async def load_check(user_id: int, user_name: str = None) -> None:
    """Функция для загрузки юзера в кэш"""
    if not users.get(user_id):
        users[user_id] = await load_user(user_id, user_name)
