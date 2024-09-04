from bot.funcs.database import algorithms_collection
from bot.api.chatbot import evaluate_answer


async def get_task(stop_list: list) -> dict:
    """
    Функция для выдачи задачки
    """
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
        self.user_code = None

    async def get_task(self) -> None:
        """
        Метод для асинхронной загрузки алгоритма
        """
        self.task = await get_task(self.stop_list)

    def get_task_id(self) -> int:
        """
        Возвращает id задачи
        """
        return self.task["_id"]

    def get_task_text(self) -> str:
        """
        Метод, возвращающий тест о задаче для пользователя
        """
        text = (f"Категория: *{self.task['Category']}*\n"
                f"Сложность: *{self.task['Difficulty']}*\n\n"
                f"[{self.task['Name']}]({self.task['Link']})")
        return text

    def get_task_solution(self) -> str:
        """
        Метод, возвращающий ссылку на решение
        """
        return self.task['Solution']

    async def check_algo_solution(self, code: str = None, feedback: bool = False) -> str:
        """
        Метод для оценки кода нейросетью
        """
        if not feedback:
            self.user_code = code
        task_text = self.task['Task']
        setting = 'algo_feedback' if feedback else 'algo_evaluate'
        score = await evaluate_answer(setting=setting, question=task_text, answer=self.user_code)
        return score


