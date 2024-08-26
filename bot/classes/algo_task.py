import pandas as pd
import os

# TODO Переделать под доставание из базы данных
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, '../../data/tables/algorithms.csv')
df_algorithms = pd.read_csv(file_path, index_col=0)


def get_task() -> dict:
    """Функция для выдачи задачки"""
    return df_algorithms.sample().to_dict(orient='records')[0]


class AlgoTask:
    """Класс для выдачи алгоритмической задачки"""

    def __init__(self) -> None:
        self.task = get_task()

    def get_task_text(self) -> str:
        """Метод, возвращающий тест о задаче для пользователя"""
        text = (f"Категория: *{self.task['Category']}*\n"
                f"Сложность: *{self.task['Difficulty']}*\n\n"
                f"[{self.task['Name']}]({self.task['Link']})")
        return text

    def get_task_solution(self) -> str:
        """Метод, возвращающий ссылку на решение"""
        return self.task['Solution']


