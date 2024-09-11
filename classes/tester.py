from time import time
from api.chatbot import evaluate_answer
from abc import ABC, abstractmethod
from motor.motor_asyncio import AsyncIOMotorCollection
import numpy as np
import random

from funcs.database import question_collection, blitz_collection

BLITZ_TIME = 60


async def generate_question(id_list: list,
                            db: AsyncIOMotorCollection = question_collection,
                            mistakes: bool = False,
                            adaptive: bool = False,
                            skills: dict | None = None
                            ) -> list | None:
    """
    Функция для генерации случайных вопросов.
    Учитывает длину теста (number) и исключение/включение вопросов по id (id_list)
    Если mistakes=True, генерирует вопросы только из id_list
    Если adaptive=True, то подстраивает вопросы под текущий уровень и слабые зоны юзера
    """

    match_condition = {"_id": {"$nin": id_list}} if not mistakes else {"_id": {"$in": id_list}}

    async def get_question(cats: list, probs: list) -> tuple[list, str]:
        """
        Вспомогательная функция для генерации вопроса
        """
        choice = random.choices(cats, weights=probs)[0]
        skill_level = skills[choice]
        difficulty = min(5, max(1, (skill_level + 1) // 2))

        match_stage = {"$match": {
            **match_condition,
            "category": choice,
            "difficulty": difficulty
        }}

        pipeline_f = ([match_stage, {"$sample": {"size": 1}}])
        random_question_cursor_f = db.aggregate(pipeline_f)
        random_question_f = await random_question_cursor_f.to_list(length=1)
        return random_question_f, choice

    if adaptive and skills:
        skill_levels = np.array(list(skills.values()))
        max_skill_level = 10
        inverse_levels = max_skill_level - skill_levels
        probabilities = inverse_levels / np.sum(inverse_levels)

        categories = list(skills.keys())
        random_question, chosen_category = await get_question(categories, probabilities)

        while not random_question and categories:
            try:
                index_to_remove = categories.index(chosen_category)
                categories.pop(index_to_remove)
                probabilities = np.delete(probabilities, index_to_remove)

                if not categories:
                    return None

                random_question, chosen_category = await get_question(categories, list(probabilities))
            except (ValueError, IndexError):
                return None

        return random_question if random_question else None

    else:
        pipeline = [
            {"$match": match_condition},
            {"$sample": {"size": 1}}
        ]
    random_question_cursor = db.aggregate(pipeline)
    random_question = await random_question_cursor.to_list(length=1)

    return random_question


def ask_question(question: dict) -> tuple[str, str]:
    """
    Функция для генерации сообщения с вопросом ботом
    Так же передает id вопроса вторым элементом картежа для последующей обработки
    """
    diff_dict = {
        1: 'Easy',
        2: 'Moderate',
        3: 'Medium',
        4: 'Hard',
        5: 'Expert'
    }

    formatted_question = (
        f"```{question['category']}\n"
        f"Difficulty: {diff_dict.get(question['difficulty'])}\n\n"
        f"{question['question']}"
        f"```"
    )

    return formatted_question, question['_id']


def ask_blitz_question(question: dict) -> tuple[str, str, dict]:
    """
    Функция для генерации текста для вопроса блиц.
    Возвращает текст вопроса, id и словарь с ответами
    """
    return f"{question['question']}", question['_id'], question['answers']


class Test(ABC):
    """
    Абстрактный родительский класс для создания разных вариантов тестирований
    """

    def __init__(self) -> None:
        """
        Инициализация класса

        Атрибуты
        ________
        self.test_score - Набранные баллы за тест
        self.current_question - Текущий вопрос
        self.user_answers - Список для хранения ответов пользователя
        """
        self.test_score = 0
        self.current_question = None
        self.last_answer = None

    def get_name(self) -> str:
        """
        Метод для получения названия класса (используется для различения разных видов тестов)
        """
        return self.__class__.__name__

    async def check_answer(self, answer: str, skip: bool = False) -> tuple[str, int, str]:
        """
        Метод оценки ответа на вопрос с помощью нейросетки
        """
        if skip:
            return self.current_question['_id']

        self.last_answer = answer
        question = self.current_question['question']
        correct_answer = self.current_question['answer']

        bot_answer = await evaluate_answer(setting='task_evaluate',
                                           question=question,
                                           answer=answer,
                                           correct_answer=correct_answer)
        bot_answer = int(bot_answer)
        self.test_score += bot_answer
        return f'{bot_answer}/5', self.current_question['_id'], self.current_question['category']

    async def give_feedback(self) -> str:
        """
        Метод для получения фидбэка на ответ (опять же нейросеткой)
        """
        question = self.current_question['question']
        correct_answer = self.current_question['answer']
        bot_answer = await evaluate_answer(setting='task_feedback',
                                           question=question,
                                           answer=self.last_answer,
                                           correct_answer=correct_answer)
        return bot_answer

    def show_correct_answer(self) -> str:
        """
        Возврат правильного ответа
        """
        return self.current_question['answer']

    @abstractmethod
    async def next_question(self, *args, **kwargs) -> any:
        """Абстрактный метод, достающий следующий вопрос теста"""
        pass


class BasicTest(Test):
    """
    Класс "Базового теста"
    """

    def __init__(self, user_skills: dict) -> None:
        """
        Инициализация класса

        Атрибуты
        ________
        self.id_list = Список вопросов, которые пользователь уже получал
        """
        super().__init__()
        self.user_skills = user_skills

    async def next_question(self, id_list: list) -> tuple[str, str] | None:
        """
        Метод, задающий вопрос (так же передает id вопроса)
        """
        questions = await generate_question(id_list=id_list,
                                            db=question_collection,
                                            adaptive=True,
                                            skills=self.user_skills)
        try:
            self.current_question = questions[0]
            return ask_question(self.current_question)
        except (IndexError, TypeError):
            return None


class BlitzTest(Test):
    """
    Класс блиц-теста
    """

    def __init__(self):
        """
        Инициализация класса

        Атрибуты
        ________
        self.start_time - Время начала тестирования
        self.used_questions - Пустой список для хранения id уже заданных вопросов
        в рамках текущего теста
        """
        super().__init__()
        self.start_time = time()
        self.used_questions = []

    async def next_question(self) -> tuple[str, str, dict]:
        """
        Метод, передающий информацию об оставшемся времени
        и задающий вопрос (так же передает id вопроса)
        """
        current_question_async = await generate_question(id_list=self.used_questions,
                                                         db=blitz_collection)
        self.current_question = current_question_async[0]
        self.used_questions.append(self.current_question['_id'])
        message = ask_blitz_question(self.current_question)

        return (
            f"```{BLITZ_TIME - round(time() - self.start_time)}\n"
            f"Score: {self.test_score}\n\n"
            f"{message[0] + ' ' * (60 - (len(message[0])))}🤔"
            f"```",
            message[1],
            message[2]
        )

    def get_category(self) -> str:
        """
        Метод для получения категории вопроса в блице
        """
        return self.current_question['category']

    def test_result(self) -> str:
        return f"```Score\n{self.test_score}```"

    def is_completed(self) -> bool:
        """
        Метод, проверяющий осталось ли еще время
        """
        return time() - self.start_time >= BLITZ_TIME

    def check_answer(self, answer: str, skip: bool = False) -> tuple[str, int, str]:
        """
        В блице проверка вопроса идет на уровне хэндлера
        """
        pass


class MistakeTest(Test):
    """
    Класс теста "работа над ошибками"
    """

    def __init__(self) -> None:
        """
        Инициализация класса, тут ничего нового не добавляется
        """
        super().__init__()
        self.shown_questions = set()

    async def next_question(self, id_list: list) -> tuple[str, str] | None:
        """
        Задаем вопрос из списка тех, на которые пользователь неидеально ответил
        """
        id_list = [number for number in id_list if number not in self.shown_questions]
        question = await generate_question(id_list=id_list, mistakes=True)
        if not question:
            return None
        self.current_question = question[0]
        self.shown_questions.add(self.current_question['_id'])
        return ask_question(self.current_question)
