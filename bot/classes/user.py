from bot.classes.tester import Test


class User:
    def __init__(self, user_id: int, info_json: dict):
        self.user_id = user_id
        self.test = None
        self.user_info = info_json

    def start_test(self, q_amount: int):
        self.test = Test(q_amount=q_amount, stop_list=self.user_info['questions_ids'])

    def answer_question(self, answer: str):
        if self.test:
            self.user_info['amount_asked'] += 1
            return self.test.check_answer(answer)
        return False

    def get_next_question(self):
        if self.test:
            question = self.test.next_question()
            self.user_info['questions_ids'].append(question[1])
            return question[0]
        return None

    def test_completed(self):
        if self.test:
            return self.test.is_completed()
        return True

    def get_score(self):
        if self.test:
            return self.test.correct_answers
        return 0

    def stats(self):
        return (f"Вы ответили на {self.user_info['amount_asked']} вопросов\n"
                f"id вопросов {self.user_info['questions_ids']}")

    def clear_data(self):
        self.user_info['amount_asked'] = 0
        self.user_info['questions_ids'] = []

