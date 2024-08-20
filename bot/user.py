from test import Test


class User:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.test = None

    def start_test(self):
        self.test = Test()

    def answer_question(self, answer: str):
        if self.test:
            return self.test.check_answer(answer)
        return False

    def get_next_question(self):
        if self.test:
            return self.test.next_question()
        return None

    def test_completed(self):
        if self.test:
            return self.test.is_completed()
        return True

    def get_score(self):
        if self.test:
            return self.test.correct_answers
        return 0

    def test_len(self):
        if self.test:
            return self.test.q_amount
        return 0
