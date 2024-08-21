import pandas as pd


question_list = pd.read_csv('../data/questions.csv')


class Test:
    def __init__(self, q_amount):
        self.q_amount = q_amount
        self.questions = question_list.sample(q_amount).to_dict(orient='records')
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

