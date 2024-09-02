from time import time
from bot.api.chatbot import evaluate_answer
from abc import ABC, abstractmethod
from bot.funcs.database import question_collection, blitz_collection
from motor.motor_asyncio import AsyncIOMotorCollection

BLITZ_TIME = 30


async def generate_questions_sample(stop_list: list,
                                    number: int = 1,
                                    db: AsyncIOMotorCollection = question_collection,
                                    mistakes: bool = False) -> list:
    """
    Функция для генерации случайных вопросов.
    Учитывает длину теста (number) и исключение вопросов по id (stop_list)
    Если mistakes=True, генерирует вопросы только из stop_list
    """

    match_condition = {"_id": {"$nin": stop_list}} if not mistakes else {"_id": {"$in": stop_list}}
    pipeline = [
        {"$match": match_condition},
        {"$sample": {"size": number}}
    ]
    random_question_cursor = db.aggregate(pipeline)
    random_questions = await random_question_cursor.to_list(length=number)
    return random_questions


def ask_question(question: dict) -> tuple[str, str]:
    """
    Функция для генерации сообщения с вопросом ботом
    Так же передает id вопроса вторым элементом картежа для последующей обработки
    """
    return (f"Категория: {question['category']}\n"
            f"Сложность: {question['difficulty']}\n\n"
            f"{question['question']}", question['_id'])


def ask_blitz_question(question: dict) -> tuple[str, str, dict]:
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
        self.current_question_index - Индекс текущего вопроса
        self.test_score - Набранные баллы за тест
        self.current_question - Текущий вопрос
        self.user_answers - Список для хранения ответов пользователя
        """
        self.current_question_index = 0
        self.test_score = 0
        self.current_question = None
        self.last_answer = None

    def get_name(self) -> str:
        """
        Метод для получения названия класса (используется для различения разных видов тестов)
        """
        return self.__class__.__name__

    def check_answer(self, answer: str) -> tuple[str, int]:
        """Метод оценки ответа"""
        self.last_answer = answer
        question = self.current_question['question']
        correct_answer = self.current_question['answer']

        bot_answer = int(evaluate_answer(question, answer, correct_answer, feedback=False))
        # bot_answer = 5
        self.test_score += bot_answer
        return f'{bot_answer}/5', self.current_question['_id']

    def give_feedback(self) -> str:
        """Метод для получения фидбэка на ответ"""
        question = self.current_question['question']
        correct_answer = self.current_question['answer']
        bot_answer = evaluate_answer(question, self.last_answer, correct_answer, feedback=True)
        return bot_answer

    def test_result(self) -> str:
        """Метод вывода результатов теста"""
        return (f"Тест завершён! Результат "
                f"{round((self.test_score / (self.current_question_index * 5)) * 100)}/100")

    @abstractmethod
    def next_question(self):
        """Абстрактный метод достающий следующий вопрос теста"""
        pass

    @abstractmethod
    def is_completed(self):
        """Абстрактный метод проверяющий тест на завершенность"""
        pass


class BasicTest(Test):
    """
    Класс "Базового теста"
    """

    def __init__(self, stop_list: list, q_amount: int) -> None:
        """
        Инициализация класса

        Атрибуты
        ________
        self.q_amount - Количество вопросов в тесте
        self.questions - Словарь с вопросами теста
        """
        super().__init__()
        self.q_amount = q_amount
        self.stop_list = stop_list
        self.questions = []

    async def initialize_questions(self) -> None:
        """Асинхронный метод для генерации теста"""
        questions = await generate_questions_sample(number=self.q_amount,
                                                    stop_list=self.stop_list,
                                                    db=question_collection)
        self.questions = questions

    async def next_question(self) -> tuple[str, str]:
        """Метод, задающий вопрос (так же передает id вопроса)"""
        self.current_question = self.questions[self.current_question_index]
        self.current_question_index += 1
        return ask_question(self.current_question)

    def is_completed(self) -> bool:
        """Метод, проверяющий остались ли еще вопросы"""
        return self.current_question_index >= len(self.questions)


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
        current_question_async = await generate_questions_sample(stop_list=self.used_questions,
                                                                 number=1,
                                                                 db=blitz_collection)
        self.current_question = current_question_async[0]
        message = ask_blitz_question(self.current_question)
        return (f'*{BLITZ_TIME - round(time() - self.start_time)} секунд*\n'
                f'*Счет: {self.test_score}*\n\n{message[0]}', message[1], message[2])

    def check_answer(self, answer: str) -> str:
        """У блица проверка на уровне хэндлера"""
        pass

    def test_result(self) -> str:
        return f"Результат: *{self.test_score}*"

    def is_completed(self) -> bool:
        """Метод, проверяющий осталось ли еще время"""
        return time() - self.start_time >= BLITZ_TIME


class MistakeTest(Test):
    """
    Класс теста "работа над ошибками"
    """
    def __init__(self, q_list: list) -> None:
        """Q_list - список из id вопросов, на которые юзер отвечал неидеально"""
        super().__init__()
        self.questions = q_list

    async def next_question(self) -> tuple[str, str]:
        """Задаем вопрос из списка тех, на которые пользователь неидеально ответил"""
        question = await generate_questions_sample(stop_list=self.questions, mistakes=True)
        self.current_question = question[0]
        return ask_question(self.current_question)

    def is_completed(self) -> bool:
        """Метод проверяющий тест на завершенность. Всегда дает True, так как в тесте всегда один вопрос"""
        return True

    def test_result(self) -> str:
        if self.test_score == 5:
            return 'Прекрасно справился!'
        else:
            return f'Пока еще не идеально'
