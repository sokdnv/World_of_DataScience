from bot.funcs.database import algorithms_collection


async def get_task(stop_list: list) -> dict:
    """Функция для выдачи задачки"""
    pipeline = [
        {"$match": {"_id": {"$nin": stop_list}}},
        {"$sample": {"size": 1}}
    ]
    random_algo_cursor = algorithms_collection.aggregate(pipeline)
    random_algo = await random_algo_cursor.to_list(length=1)
    return random_algo[0]


class AlgoTask:
    """Класс для выдачи алгоритмической задачки"""

    def __init__(self, stop_list: list) -> None:
        self.stop_list = stop_list
        self.task = None

    async def get_task(self) -> None:
        """Метод для асинхронной загрузки алгоритма"""
        self.task = await get_task(self.stop_list)

    def get_task_id(self) -> int:
        """Возвращает id задачи"""
        return self.task["_id"]

    def get_task_text(self) -> str:
        """Метод, возвращающий тест о задаче для пользователя"""
        text = (f"Категория: *{self.task['Category']}*\n"
                f"Сложность: *{self.task['Difficulty']}*\n\n"
                f"[{self.task['Name']}]({self.task['Link']})")
        return text

    def get_task_solution(self) -> str:
        """Метод, возвращающий ссылку на решение"""
        return self.task['Solution']


