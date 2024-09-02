from motor.motor_asyncio import AsyncIOMotorClient
from bot.config_reader import config

client = AsyncIOMotorClient(config.DB_KEY.get_secret_value())
db = client['mentor_db']
user_collection = db.users
question_collection = db.basic_test
blitz_collection = db.blitz_test
algorithms_collection = db.algorithms

blank_user_data = {
    '_id': int,
    'name': str,
    'nickname': None,
    'character': None,
    'rating': {
        'python': 0,
        'algorithms': 0,
        'SQL': 0,
        'ML': 0,
        'DL': 0,
        'mathematics': 0
    },
    'achievements': {
        'total_blitz_test': 0,
        'total_resources': 0,
        'total_alg_tasks': 0,
        'total_news': 0,
        'total_vacancy': 0
    },
    'history': {
        'solved_basic_tasks_perfect': [],
        'solved_basic_tasks_not_perfect': [],
        'solved_algo_tasks': [],
        'articles_read': [],
        'blitz_record': 0
    }
}


async def add_user_to_db(user_id: int, name: str, force: bool = False):
    """
    Добавляет пользователя в базу данных с начальными данными.
    """
    existing_user = await user_collection.find_one({"_id": user_id})
    data = blank_user_data.copy()
    data.update({'_id': user_id, 'name': name})

    if existing_user:
        if force:
            await user_collection.replace_one({"_id": user_id}, data)
    else:
        await user_collection.insert_one(data)

    return data

