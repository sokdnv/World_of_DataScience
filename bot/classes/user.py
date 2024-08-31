from bot.classes.tester import BasicTest, BlitzTest
from bot.funcs.database import add_user_to_db
from bot.classes.algo_task import AlgoTask
from bot.funcs.database import user_collection


async def find_data(user_id: int, key: str | None = None) -> any:
    """Функция для поиска данных по базе данных"""
    projection = {key: 1} if key else None
    result = await user_collection.find_one({"_id": user_id}, projection)

    return result


class User:
    """
    Класс пользователя
    """

    def __init__(self, user_id: int):
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

    async def start_basic_test(self, q_amount: int) -> None:
        """Метод для создания обычного теста"""
        data = await find_data(user_id=self.user_id, key="history.solved_basic_tasks")
        self.test = BasicTest(stop_list=data['history']['solved_basic_tasks'],
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
            await user_collection.update_one(
                {'_id': self.user_id},
                {'$push': {'history.solved_basic_tasks': question[1]}}
            )
            return question[0]
        elif self.test.get_name() == 'BlitzTest':
            return question[0], question[2]

    async def test_completed(self) -> bool:
        """Метод для проверки окончания теста"""
        completion = self.test.is_completed()
        if completion:
            if self.test.get_name() == 'BasicTest':
                await user_collection.update_one(
                    {'_id': self.user_id},
                    {'$inc': {'achievements.total_basic_test': 1}}
                )
            elif self.test.get_name() == 'BlitzTest':
                await user_collection.update_one(
                    {'_id': self.user_id},
                    {'$inc': {'achievements.total_blitz_test': 1}}
                )
        return completion

    async def stats(self) -> str:
        """Метод для вывода статистики пользователя"""
        data = await find_data(user_id=self.user_id)
        return (f"Вы завершили\n{data['achievements']['total_basic_test']} обычных тестов\n"
                f"{data['achievements']['total_blitz_test']} блиц тестов\n"
                f"id обычных вопросов: {data['history']['solved_basic_tasks']}\n"
                f"id алгоритмических задач {data['history']['solved_algo_tasks']}")

    async def clear_data(self) -> None:
        """Метод для очистки информации о пользователе"""
        await add_user_to_db(self.user_id, name='Cleared_by_force', force=True)

    async def get_algo_task(self) -> None:
        """Метод для выдачи алгоритмической задачки"""
        data = await find_data(user_id=self.user_id, key="history.solved_algo_tasks")
        self.test = AlgoTask(stop_list=data['history']['solved_algo_tasks'])
        await self.test.get_task()
        await user_collection.update_one(
            {'_id': self.user_id},
            {'$push': {'history.solved_algo_tasks': self.test.get_task_id()}}
        )

    async def get_blitz_record(self) -> int:
        """Возвращаем блиц рекорд юзера"""
        data = await find_data(user_id=self.user_id, key="history.blitz_record")
        return data['history']['blitz_record']

    async def set_blitz_record(self, record: int) -> None:
        """Обновляем блиц рекорд юзера"""
        await user_collection.update_one(
            {'_id': self.user_id},
            {'$set': {'history.blitz_record': record}}
        )

    async def set_character(self, nickname: str, character: str) -> None:
        """Вводим информацию о никнейме / классе пользователя"""
        await user_collection.update_one(
            {'_id': self.user_id},
            {'$set': {'nickname': nickname, 'character': character}}
        )

