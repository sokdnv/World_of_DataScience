from bot.util.config import CHAT_API
from langchain.chat_models.gigachat import GigaChat
from langchain.schema import HumanMessage, SystemMessage

chat = GigaChat(credentials=CHAT_API,
                verify_ssl_certs=False)

setting = ("Ты оцениваешь тест по Data Science. Дать оценку ответу от 0 до 5"
           "если ты оценил меньше, чем на 5, то дать краткий комментарий"
           "человеческим языком,что именно можно было бы улучшить в ответе"
           "игнорируй орфографические ошибки"
           "Структура твоего ответа: "
           "(твой балл)/5 (пробел) Комментарий:")

messages = [
    SystemMessage(
        content=setting
    )
]


def evaluate_answer(question: str, answer: str, correct_answer: str):
    user_input = (f"вопрос: '{question}'. "
                  f"ответ для оценки: '{answer}'. "
                  f"правильный ответ для сверки: '{correct_answer}'")
    messages.append(HumanMessage(content=user_input))
    res = chat.invoke(messages)
    messages.append(res)
    return res.content
