import pandas as pd

Q_AMOUNT = 3

df = pd.read_csv('../data/test_q.csv', sep=';')
questions = df.sample(Q_AMOUNT).to_dict(orient='records')


class Test:
    def __init__(self):
        self.q_amount = Q_AMOUNT
        self.questions = questions
        self.current_question_index = 0
        self.correct_answers = 0

    def next_question(self):
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]['Вопрос']
        return None

    def check_answer(self, answer: str):
        current_question = self.questions[self.current_question_index]
        if answer.strip().lower() == str(current_question['Ответ']).strip().lower():
            self.correct_answers += 1
            return True
        return False

    def is_completed(self):
        return self.current_question_index >= len(self.questions)

    def increment_question(self):
        self.current_question_index += 1
