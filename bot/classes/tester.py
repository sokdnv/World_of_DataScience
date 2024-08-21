import os
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, '../../data/tables/questions.csv')

question_list = pd.read_csv(file_path, index_col=0)


def generate_basic_test(number, stop_list):
    filtered_questions = question_list[~question_list['id'].isin(stop_list)]
    sample_questions = filtered_questions.sample(n=number)
    return sample_questions.to_dict(orient='records')


class Test:
    def __init__(self, q_amount, stop_list):
        self.q_amount = q_amount
        self.questions = generate_basic_test(number=q_amount, stop_list=stop_list)
        self.current_question_index = 0
        self.correct_answers = 0

    def next_question(self):
        if self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            return (f"Категория: {question['category']}\n"
                    f"Сложность: {question['difficulty']}\n\n"
                    f"{question['question']}", question['id'])
        return None

    def check_answer(self, answer: str):
        current_question = self.questions[self.current_question_index]
        if answer.strip().lower() == str(current_question['answer']).strip().lower():
            self.correct_answers += 1
            return True
        return False

    def is_completed(self):
        return self.current_question_index >= len(self.questions)

    def increment_question(self):
        self.current_question_index += 1

    def test_result(self):
        return f"Тест завершён! Вы ответили правильно на {self.correct_answers} из {self.q_amount} вопросов."

