from motor.motor_asyncio import AsyncIOMotorClient
from bot.config_reader import config
from PIL import Image, ImageDraw, ImageFont
import io
from aiogram.types import BufferedInputFile

client = AsyncIOMotorClient(config.DB_KEY.get_secret_value())
db = client['mentor_db']
user_collection = db.users
question_collection = db.basic_test
blitz_collection = db.blitz_test
algorithms_collection = db.algorithms
image_collection = db.images

blank_user_data = {
    '_id': int,
    'name': str,
    'nickname': None,
    'character': None,
    'total_level': 0,
    'exp_points': {
        'python': 0,
        'algorithms': 0,
        'SQL': 0,
        'ML': 0,
        'DL': 0,
        'math': 0
    },
    'achievements': {
        'total_blitz_test': 0,
        'total_alg_tasks': 0,
        'blitz_record': 0,
        'total_perfect_answers': 0
    },
    'history': {
        'solved_basic_tasks': {},
        'solved_algo_tasks': [],
        'articles_read': []
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


async def top_players() -> BufferedInputFile:
    """
    Функция для генерации топа по уровню
    """
    top_users = await user_collection.find(
        {},
        {"nickname": 1, "total_level": 1, "_id": 0}
    ).sort("total_level", -1).limit(10).to_list(length=10)

    image_document = await image_collection.find_one({"image_name": "leaderboard.png"})
    binary_image_data = image_document['image_data']
    image_stream = io.BytesIO(binary_image_data)
    result_image = Image.open(image_stream).convert("RGBA")

    draw = ImageDraw.Draw(result_image)
    font_small = ImageFont.truetype('image_gen/font.ttf', size=55)
    font_mid = ImageFont.truetype('image_gen/font.ttf', size=85)
    font_big = ImageFont.truetype('image_gen/font.ttf', size=120)

    yellow = (213, 239, 78, 255)
    colors = [
        (255, 165, 0, 255),  # Оранжевый
        (255, 0, 0, 255),  # Красный
        (255, 192, 203, 255),  # Розовый
        (0, 0, 255, 255),  # Синий
        (0, 210, 210, 255),  # Бирюзовый
    ]

    draw.text((280, 50), "TOP PLAYERS", font=font_big, fill=yellow)
    draw.text((155, 250), "RANK", font=font_mid, fill=yellow)
    draw.text((390, 250), "NAME", font=font_mid, fill=yellow)
    draw.text((780, 250), "LEVEL", font=font_mid, fill=yellow)

    start = 360
    rank = 1
    for i, user in enumerate(top_users):
        color = colors[i % len(colors)]
        draw.text((155, start), str(rank), font=font_small, fill=color)
        draw.text((390, start), user['nickname'], font=font_small, fill=color)
        draw.text((780, start), str(user['total_level']), font=font_small, fill=color)

        rank += 1
        start += 45

    image_buffer = io.BytesIO()
    result_image.save(image_buffer, format='PNG')
    image_buffer.seek(0)
    photo_bytes = image_buffer.read()

    return BufferedInputFile(file=photo_bytes, filename='top_players')


async def top_blitz() -> BufferedInputFile:
    """
    Функция для генерации топа по блицам
    """
    top_users = await user_collection.find(
        {},
        {"nickname": 1, "achievements.blitz_record": 1, "_id": 0}
    ).sort("achievements.blitz_record", -1).limit(10).to_list(length=10)

    image_document = await image_collection.find_one({"image_name": "leaderboard.png"})
    binary_image_data = image_document['image_data']
    image_stream = io.BytesIO(binary_image_data)
    result_image = Image.open(image_stream).convert("RGBA")

    draw = ImageDraw.Draw(result_image)
    font_small = ImageFont.truetype('image_gen/font.ttf', size=55)
    font_mid = ImageFont.truetype('image_gen/font.ttf', size=85)
    font_big = ImageFont.truetype('image_gen/font.ttf', size=120)

    yellow = (213, 239, 78, 255)
    colors = [
        (255, 165, 0, 255),  # Оранжевый
        (255, 0, 0, 255),  # Красный
        (255, 192, 203, 255),  # Розовый
        (0, 0, 255, 255),  # Синий
        (0, 210, 210, 255),  # Бирюзовый
    ]

    draw.text((147, 50), "BLITZ LEADERBOARD", font=font_big, fill=yellow)
    draw.text((155, 250), "RANK", font=font_mid, fill=yellow)
    draw.text((390, 250), "NAME", font=font_mid, fill=yellow)
    draw.text((780, 250), "SCORE", font=font_mid, fill=yellow)

    start = 360
    rank = 1
    for i, user in enumerate(top_users):
        color = colors[i % len(colors)]
        draw.text((155, start), str(rank), font=font_small, fill=color)
        draw.text((390, start), user['nickname'], font=font_small, fill=color)
        draw.text((780, start), str(user['achievements']['blitz_record']), font=font_small, fill=color)

        rank += 1
        start += 45

    image_buffer = io.BytesIO()
    result_image.save(image_buffer, format='PNG')
    image_buffer.seek(0)
    photo_bytes = image_buffer.read()

    return BufferedInputFile(file=photo_bytes, filename='top_blitz')
