from bot.classes.tester import BasicTest, BlitzTest
from bot.funcs.database import add_user_to_db
from bot.classes.algo_task import AlgoTask


class User:
    """
    Класс пользователя
    """

    def __init__(self, user_id: int, user_data: dict):
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
        self.user_data = user_data

    def start_basic_test(self, q_amount: int) -> None:
        """Метод для создания обычного теста"""
        self.test = BasicTest(stop_list=self.user_data['history']['solved_basic_tasks'],
                              q_amount=q_amount)

    def start_blitz_test(self) -> None:
        """Метод для создания обычного теста"""
        self.test = BlitzTest()

    def answer_question(self, answer: str) -> str:
        """Метод для ответа на вопрос"""
        return self.test.check_answer(answer)

    async def get_next_question(self) -> tuple[str, dict] | str:
        """
        Метод для доставания следующего вопроса из теста
        так же добавляет id вопроса в список заданных вопросов пользователю
        """
        question = await self.test.next_question()
        if self.test.get_name() == 'BasicTest':
            self.user_data['history']['solved_basic_tasks'].append(question[1])
            return question[0]
        elif self.test.get_name() == 'BlitzTest':
            return question[0], question[2]

    def test_completed(self) -> bool:
        """Метод для проверки окончания теста"""
        completion = self.test.is_completed()
        if completion:
            if self.test.get_name() == 'BasicTest':
                self.user_data['achievements']['total_basic_test'] += 1
            elif self.test.get_name() == 'BlitzTest':
                self.user_data['achievements']['total_blitz_test'] += 1
        return completion

    def stats(self) -> str:
        """Метод для вывода статистики пользователя"""
        return (f"Вы завершили\n{self.user_data['achievements']['total_basic_test']} обычных тестов\n"
                f"{self.user_data['achievements']['total_blitz_test']} блиц тестов\n"
                f"id обычных вопросов: {self.user_data['history']['solved_basic_tasks']}\n"
                f"id алгоритмических задач {self.user_data['history']['solved_algo_tasks']}")

    async def clear_data(self) -> None:
        """Метод для очистки информации о пользователе"""
        self.user_data = await add_user_to_db(self.user_id, name='Cleared_by_force', force=True)

    async def get_algo_task(self) -> None:
        """Метод для выдачи алгоритмической задачки"""
        self.test = AlgoTask(stop_list=self.user_data['history']['solved_algo_tasks'])
        await self.test.get_task()
        self.user_data['history']['solved_algo_tasks'].append(self.test.get_task_id())
