import os
import pandas as pd
from time import time
from random import randint
from bot.app.chatbot import evaluate_answer
from abc import ABC, abstractmethod

current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, '../../data/tables/questions.csv')

question_list = pd.read_csv(file_path, index_col=0)

BLITZ_TIME = 30


def generate_basic_test(number: int, stop_list: list) -> dict:
    """
    Функция для генерации обычного теста.
    Учитывает длину теста (number) и исключение вопросов по id (stop_list)
    """
    filtered_questions = question_list[~question_list['id'].isin(stop_list)]
    sample_questions = filtered_questions.sample(n=number)
    return sample_questions.to_dict(orient='records')


def generate_random_question(stop_list: list) -> dict:
    """
    Функция для генерации случайного вопроса из теста.
    Исключает id вопросов из stop_list
    """
    while True:
        question_id = randint(0, question_list.shape[0] - 1)
        if question_id not in stop_list:
            break
    return question_list.iloc[question_id].to_dict()


def ask_question(question: dict) -> tuple[str, str]:
    """
    Функция для генерации сообщения с вопросом ботом
    Так же передает id вопроса вторым элементом картежа для последующей обработки
    """
    return (f"Категория: {question['category']}\n"
            f"Сложность: {question['difficulty']}\n\n"
            f"{question['question']}", question['id'])


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
        """
        self.current_question_index = 0
        self.test_score = 0
        self.current_question = None

    def get_name(self) -> str:
        """
        Метод для получения названия класса (используется для различения разных видов тестов)
        """
        return self.__class__.__name__

    def check_answer(self, answer: str) -> str:
        """
        Метод проверки ответа на тест
        """
        question = self.current_question['question']
        correct_answer = self.current_question['answer']
        bot_answer = evaluate_answer(question, answer, correct_answer)
        self.test_score += int(bot_answer[0])
        self.current_question_index += 1
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
        self.questions = generate_basic_test(number=q_amount, stop_list=stop_list)

    def next_question(self) -> tuple[str, str]:
        """Метод, задающий вопрос (так же передает id вопроса)"""
        self.current_question = self.questions[self.current_question_index]
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

    def next_question(self) -> tuple[str, str]:
        """
        Метод, передающий информацию об оставшемся времени
        и задающий вопрос (так же передает id вопроса)
        """
        self.current_question = generate_random_question(stop_list=self.used_questions)
        message = ask_question(self.current_question)
        return f'Осталось {BLITZ_TIME - round(time() - self.start_time)} секунд\n\n{message[0]}', message[1]

    def is_completed(self) -> bool:
        """Метод, проверяющий осталось ли еще время"""
        return time() - self.start_time >= BLITZ_TIME
