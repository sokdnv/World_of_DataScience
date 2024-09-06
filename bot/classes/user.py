from typing import Any

from PIL import Image, ImageDraw, ImageFont
import io
from aiogram.types import BufferedInputFile

from bot.classes.tester import BasicTest, BlitzTest, MistakeTest
from bot.funcs.database import add_user_to_db
from bot.classes.algo_task import AlgoTask
from bot.funcs.database import user_collection


async def find_data(user_id: int, key: str | None = None) -> any:
    """
    Функция для поиска данных по базе данных
    """
    projection = {key: 1} if key else None
    result = await user_collection.find_one({"_id": user_id}, projection)

    return result


class User:
    """
    Класс пользователя
    """

    def __init__(self, user_id: int):
        """
        Инициализация класса

        Атрибуты
        ________
        self.user_id - id пользователя в телеграмме
        self.test - Место под экземпляры различных тестов
        self.skills - текущие уровни умений
        """
        self.user_id = user_id
        self.test = None
        self.skills = None

    async def start_basic_test(self) -> None:
        """
        Метод для создания обычного теста
        """
        if not self.skills:
            await self.set_levels()

        self.test = BasicTest(user_skills=self.skills)

    def start_blitz_test(self) -> None:
        """
        Метод для создания обычного теста
        """
        self.test = BlitzTest()

    async def answer_question(self, answer: str = None, skip: bool = False) -> str | None:
        """
        Метод для ответа на вопрос и начисления опыта
        """
        score = await self.test.check_answer(answer, skip=skip)
        if skip:
            await user_collection.update_one(
                {'_id': self.user_id},
                {'$set': {f'history.solved_basic_tasks.{score}': 0}}
            )
            return

        test_name = self.test.get_name()
        updates = {}
        mark = int(score[0][0])

        if test_name == 'BasicTest':
            await self.get_basic_exp(category=score[2], score=mark)

        if test_name == 'MistakeTest':
            if mark == 5:
                await self.get_basic_exp(category=score[2], score=mark)

        updates['$set'] = {f'history.solved_basic_tasks.{score[1]}': mark}

        if mark == 5:
            updates['$inc'] = {'achievements.total_perfect_answers': 1}

        if updates:
            await user_collection.update_one({'_id': self.user_id}, updates)

        return score[0]

    async def get_next_question(self) -> tuple[str, dict] | str | bool:
        """
        Метод для доставания следующего вопроса из теста
        так же добавляет id вопроса в список заданных вопросов пользователю
        """
        test_name = self.test.get_name()

        if test_name == 'BasicTest':

            data = await find_data(user_id=self.user_id, key="history.solved_basic_tasks")
            solved = [int(key) for key in data['history']['solved_basic_tasks'].keys()]
            question = await self.test.next_question(id_list=solved)
            if question:
                return question[0]
            return False

        if test_name == 'MistakeTest':

            data = await find_data(user_id=self.user_id, key="history.solved_basic_tasks")
            not_perfect = [int(key) for key, value in data['history']['solved_basic_tasks'].items() if value != 5]
            if not not_perfect:
                return False
            question = await self.test.next_question(id_list=not_perfect)

            return question[0]

        if test_name == 'BlitzTest':

            question = await self.test.next_question()

            return question[0], question[2]

    async def test_completed(self) -> bool:
        """
        Метод для проверки окончания блиц теста
        """
        completion = False
        if self.test.get_name() == 'BlitzTest':
            completion = self.test.is_completed()
            if completion:
                await user_collection.update_one(
                    {'_id': self.user_id},
                    {'$inc': {'achievements.total_blitz_test': 1}}
                )
        return completion

    async def clear_data(self) -> None:
        """
        Черновой метод для очистки информации о пользователе
        """
        await add_user_to_db(self.user_id, name='Cleared_by_force', force=True)

    async def get_algo_task(self) -> None:
        """
        Метод для выдачи алгоритмической задачки
        """
        data = await find_data(user_id=self.user_id, key="history.solved_algo_tasks")
        skills, _, _ = await self.calculate_levels()
        algo_level = skills['algorithms'][0]
        if 0 <= algo_level <= 2:
            level = 'Easy'
        elif 3 <= algo_level <= 7:
            level = 'Medium'
        else:
            level = 'Hard'
        self.test = AlgoTask(stop_list=data['history']['solved_algo_tasks'], level=level)
        await self.test.get_task()

    async def algo_task_solved(self, fail: False) -> None:
        """
        Метод для изменения данных в базе знаний при решении алгоритмических задач
        """
        update_query = {
            '$push': {'history.solved_algo_tasks': self.test.get_task_id()}
        }

        if not fail:
            update_query['$inc'] = {'achievements.total_alg_tasks': 1,
                                    'exp_points.algorithms': 50}

        await user_collection.update_one(
            {'_id': self.user_id},
            update_query
        )

    async def get_blitz_record(self) -> int:
        """
        Возвращаем блиц рекорд юзера
        """
        data = await find_data(user_id=self.user_id, key="achievements.blitz_record")
        return data['achievements']['blitz_record']

    async def set_blitz_record(self, record: int) -> None:
        """
        Обновляем блиц рекорд юзера
        """
        await user_collection.update_one(
            {'_id': self.user_id},
            {'$set': {'achievements.blitz_record': record}}
        )

    async def get_basic_exp(self, category: str, score: int) -> None:
        """
        Метод для получения опыта за базовый ответ
        """
        exp_dict = {5: 20, 4: 10, 3: 5}
        exp_dict_alg = {5: 15, 4: 7, 3: 3}
        exp_basic = exp_dict_alg.get(score, 0) if category == 'algorithms' else exp_dict.get(score, 0)
        await user_collection.update_one(
            {'_id': self.user_id},
            {'$inc': {f'exp_points.{category}': exp_basic}}
        )

    async def get_blitz_exp(self) -> None:
        """
        Метод для получения опыт за правильный ответ на блиц
        """
        category = self.test.get_category()
        exp_blitz = 3 if category == 'algorithms' else 5
        await user_collection.update_one(
            {'_id': self.user_id},
            {'$inc': {f'exp_points.{category}': exp_blitz}}
        )

    async def set_character(self, nickname: str, character: str) -> None:
        """
        Вводим информацию о никнейме / классе пользователя
        """
        await user_collection.update_one(
            {'_id': self.user_id},
            {'$set': {'nickname': nickname, 'character': character}}
        )

    async def start_mistake_test(self) -> None:
        """
        Метод для старта работы над ошибками
        """
        self.test = MistakeTest()

    async def calculate_levels(self) -> tuple[dict[Any, tuple[int, Any]], int, str]:
        """
        Метод для подсчета уровней умений и общего уровня
        """
        info = await find_data(self.user_id, key="exp_points")
        experience_points = info['exp_points']
        levels = [110, 265, 470, 730, 1070, 1510, 2080, 2825, 3800, 5000]
        skills = {}

        for skill, exp in experience_points.items():
            level = 0
            progress_to_next = 0.0

            for i in range(len(levels)):
                if exp < levels[i]:
                    progress_to_next = (exp - (levels[i - 1] if i > 0 else 0)) / (
                            levels[i] - (levels[i - 1] if i > 0 else 0))
                    break
                level += 1

            skills[skill] = level, round(progress_to_next, 2)

        total_level = sum(n[0] for n in skills.values())

        role_ranges = {
            9: 'Student',
            19: 'Intern',
            29: 'Junior',
            39: 'Middle',
            49: 'Senior',
            59: 'Team Lead'
        }

        role = 'Data Lord'
        for max_level, role_name in role_ranges.items():
            if total_level <= max_level:
                role = role_name
                break

        return skills, total_level, role

    async def character_card(self) -> BufferedInputFile:
        """
        Ужасающий метод для графического отображения информации о персонаже
        """
        info = await find_data(user_id=self.user_id)
        skills, level, role = await self.calculate_levels()

        role_coords = {
            'Student': 847,
            'Team Lead': 820
        }
        role_coord = role_coords.get(role, 857)

        achieve_coords = {1: 360, 2: 344}
        progress_coords = {2: 785}

        def achieve_coord(string: str) -> int:
            return achieve_coords.get(len(string), 328)

        def progress_coord(string: str) -> int:
            return progress_coords.get(len(string), 775)

        def level_coord(level: int) -> int:
            return 1000 if level == 10 else 1020

        def chose_image(type: str, level: int) -> str:
            number = level // 10 + 1
            return f'image_gen/{type}_{number}.png'

        result_image = Image.open('image_gen/template.png').convert("RGBA")
        character_image = Image.open(chose_image(info['character'], level)).convert("RGBA")

        character_image = character_image.resize((450, 450))
        result_image.paste(character_image, (15, 15), character_image)

        font_large = ImageFont.truetype('image_gen/font.ttf', size=90)
        font_upper = ImageFont.truetype('image_gen/font.ttf', size=75)
        font_medium = ImageFont.truetype('image_gen/font.ttf', size=60)
        font_small = ImageFont.truetype('image_gen/font.ttf', size=45)

        yellow = (213, 239, 78, 255)
        grey = (74, 74, 74, 255)

        draw = ImageDraw.Draw(result_image)

        draw.text((527, 40), f'Lv.{level}', font=font_large, fill=yellow)
        draw.text((role_coord, 60), role, font=font_medium, fill=yellow)
        draw.text((527, 205), info['nickname'], font=font_large, fill='black')

        achievements = [
            ('total_blitz_test', 610),
            ('blitz_record', 732),
            ('total_alg_tasks', 890),
            ('total_perfect_answers', 1048)
        ]

        for key, y_coord in achievements:
            value = str(info['achievements'][key])
            draw.text((achieve_coord(value), y_coord), value, font=font_upper, fill=yellow)

        skill_data = [
            ('python', 382, 377, 451),
            ('algorithms', 517, 512, 586),
            ('ML', 652, 652, 721),
            ('DL', 787, 782, 856),
            ('SQL', 924, 919, 991),
            ('math', 1057, 1052, 1126)
        ]

        for skill, progress_y, level_y, line_y in skill_data:
            level_value = str(skills[skill][0])

            if skills[skill][0] == 10:
                progress_text = 'Max'
                progress_length = 518
            else:
                progress_value = str(int(skills[skill][1] * 100)) + '%'
                progress_text = progress_value
                progress_length = 518 * skills[skill][1]

            draw.text((progress_coord(progress_text), progress_y), progress_text, font=font_small, fill=grey)
            draw.text((level_coord(skills[skill][0]), level_y), level_value, font=font_medium, fill=yellow)
            draw.line([(528, line_y), (528 + progress_length, line_y)], fill=yellow, width=21)

        image_buffer = io.BytesIO()
        result_image.save(image_buffer, format='PNG')
        image_buffer.seek(0)
        photo_bytes = image_buffer.read()

        return BufferedInputFile(file=photo_bytes, filename='character')

    async def set_levels(self) -> None:
        """
        Функция для определения текущего уровня
        """
        skills, _, _ = await self.calculate_levels()
        self.skills = {key: value[0] for key, value in skills.items()}

    async def level_up_check(self) -> str | None:
        """
        Функция для определения повысился ли уровень
        """
        if not self.skills:
            await self.set_levels()
            return None

        skills, _, _ = await self.calculate_levels()
        new_levels = {key: value[0] for key, value in skills.items()}
        increases = []

        for skill, level1 in self.skills.items():
            level2 = new_levels.get(skill)
            if level1 < level2:
                increases.append(f'{skill.capitalize()} increased to lv.{level2}')

        if increases:
            total_level = sum(new_levels.values())
            increases.append(f'Total level is now lv.{total_level}!')
            self.skills = new_levels
            await user_collection.update_one(
                {'_id': self.user_id},
                {'$set': {'total_level': total_level}}
            )
            return '\n'.join(increases)

        return None

    async def get_nickname(self) -> bool:
        """
        Функция проверки, есть ли пользователь в базе данных
        """
        nickname = await find_data(user_id=self.user_id, key='nickname')
        return bool(nickname.get('nickname'))
