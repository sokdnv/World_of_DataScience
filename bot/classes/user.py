from bot.classes.tester import BasicTest, BlitzTest


class User:
    def __init__(self, user_id: int, info_json: dict):
        self.user_id = user_id
        self.test = None
        self.user_info = info_json

    def start_basic_test(self, q_amount: int):
        self.test = BasicTest(stop_list=self.user_info['questions_ids'],
                              q_amount=q_amount)

    def start_blitz_test(self):
        self.test = BlitzTest()

    def answer_question(self, answer: str):
        if self.test.get_name() == 'BasicTest':
            self.user_info['amount_basic'] += 1
        elif self.test.get_name() == 'BlitzTest':
            self.user_info['amount_blitz'] += 1
        return self.test.check_answer(answer)

    def get_next_question(self):
        if self.test:
            question = self.test.next_question()
            if self.test.get_name() == 'BasicTest':
                self.user_info['questions_ids'].append(question[1])
            return question[0]
        return None

    def test_completed(self):
        if self.test:
            return self.test.is_completed()
        return True

    def stats(self):
        return (f"Вы ответили на\n{self.user_info['amount_basic']} обычных вопросов\n"
                f"{self.user_info['amount_blitz']} блиц вопросов\n"
                f"id вопросов {self.user_info['questions_ids']}")

    def clear_data(self):
        self.user_info['amount_basic'] = 0
        self.user_info['amount_blitz'] = 0
        self.user_info['questions_ids'] = []
