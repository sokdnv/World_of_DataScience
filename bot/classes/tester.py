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


def generate_basic_test(number, stop_list):
    filtered_questions = question_list[~question_list['id'].isin(stop_list)]
    sample_questions = filtered_questions.sample(n=number)
    return sample_questions.to_dict(orient='records')


def generate_random_question(stop_list):
    while True:
        question_id = randint(0, question_list.shape[0] - 1)
        if question_id not in stop_list:
            break
    return question_list.iloc[question_id].to_dict()


def ask_question(question):
    return (f"Категория: {question['category']}\n"
            f"Сложность: {question['difficulty']}\n\n"
            f"{question['question']}", question['id'])


class Test(ABC):
    def __init__(self):
        self.current_question_index = 0
        self.test_score = 0
        self.current_question = None

    def get_name(self):
        return self.__class__.__name__

    def check_answer(self, answer: str):
        question = self.current_question['question']
        correct_answer = self.current_question['answer']
        bot_answer = evaluate_answer(question, answer, correct_answer)
        self.test_score += int(bot_answer[0])
        self.current_question_index += 1
        return bot_answer

    def test_result(self):
        return f"Тест завершён! Результат {round((self.test_score / (self.current_question_index * 5)) * 100)}/100"

    @abstractmethod
    def next_question(self):
        pass

    @abstractmethod
    def is_completed(self):
        pass


class BasicTest(Test):
    def __init__(self, stop_list, q_amount):
        super().__init__()
        self.q_amount = q_amount
        self.questions = generate_basic_test(number=q_amount, stop_list=stop_list)

    def next_question(self):
        self.current_question = self.questions[self.current_question_index]
        return ask_question(self.current_question)

    def is_completed(self):
        return self.current_question_index >= len(self.questions)


class BlitzTest(Test):
    def __init__(self):
        super().__init__()
        self.start_time = time()
        self.used_questions = []

    def next_question(self):
        self.current_question = generate_random_question(stop_list=self.used_questions)
        message = ask_question(self.current_question)
        return f'Осталось {BLITZ_TIME - round(time() - self.start_time)} секунд\n\n{message[0]}', message[1]

    def is_completed(self):
        return time() - self.start_time >= BLITZ_TIME
