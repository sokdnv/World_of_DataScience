import json
import os
from bot.classes.user import User
from bot.app.state import users


def load_user_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return {'amount_basic': 0,
            'amount_blitz': 0,
            'questions_ids': []}


def save_user_data(user):
    path = f'../data/users/{user.user_id}.json'
    with open(path, 'w') as file:
        json.dump(user.user_info, file, indent=4)


def load_user(user_id):
    path = f'../data/users/{user_id}.json'
    user_data = load_user_data(path)
    user = User(user_id=user_id, info_json=user_data)
    return user


def load_check(user_id):
    if not users.get(user_id):
        users[user_id] = load_user(user_id)
