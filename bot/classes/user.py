from bot.classes.tester import BasicTest, BlitzTest
from bot.funcs.vars import user_info_blank
from bot.classes.algo_task import AlgoTask


class User:
    """
    Класс пользователя
    """

    def __init__(self, user_id: int, info_json: dict):
        """
        Инициализация класса

        Атрибуты
        ________
        self.user_id - id пользователя в телеграмме
        self.test - Место под экземпляры различных тестов
        self.user_info - словарь с информацией о пользователе
        """
        self.user_id = user_id
        self.test = None
        self.user_info = info_json

    def start_basic_test(self, q_amount: int) -> None:
        """Метод для создания обычного теста"""
        self.test = BasicTest(stop_list=self.user_info['questions_ids'],
                              q_amount=q_amount)

    def start_blitz_test(self) -> None:
        """Метод для создания обычного теста"""
        self.test = BlitzTest()

    def answer_question(self, answer: str) -> str:
        """Метод для ответа на вопрос"""
        if self.test.get_name() == 'BasicTest':
            self.user_info['amount_basic'] += 1
        elif self.test.get_name() == 'BlitzTest':
            self.user_info['amount_blitz'] += 1
        return self.test.check_answer(answer)

    def get_next_question(self) -> str:
        """
        Метод для доставания следующего вопроса из теста
        так же добавляет id вопроса в список заданных вопросов пользователю
        """
        question = self.test.next_question()
        if self.test.get_name() == 'BasicTest':
            self.user_info['questions_ids'].append(question[1])
        return question[0]

    def test_completed(self) -> bool:
        """Метод для проверки окончания теста"""
        return self.test.is_completed()

    def stats(self) -> str:
        """Метод для вывода статистики пользователя"""
        return (f"Вы ответили на\n{self.user_info['amount_basic']} обычных вопросов\n"
                f"{self.user_info['amount_blitz']} блиц вопросов\n"
                f"id вопросов {self.user_info['questions_ids']}")

    def clear_data(self) -> None:
        """Метод для очистки информации о пользователе"""
        self.user_info = user_info_blank

    def get_algo_task(self) -> None:
        """Метод для выдачи алгоритмической задачки"""
        self.test = AlgoTask()
