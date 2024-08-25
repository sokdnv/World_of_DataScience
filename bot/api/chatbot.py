from bot.config_reader import config
from langchain.chat_models.gigachat import GigaChat
from langchain.schema import HumanMessage, SystemMessage

chat = GigaChat(credentials=config.CHAT_API.get_secret_value(),
                verify_ssl_certs=False)

# инструкции для чат-бота
setting_evaluate = (
    "Ты оцениваешь тест по Data Science. Тебе нужно дать оценку ответу от 0 до 5"
    "игнорируй орфографические ошибки. ответь одним числом"
)

setting_feedback = (
    "Ты оцениваешь тест по Data Science. Ты должен дать человеческим языком "
    "и обращаясь на 'ты' отзыв по полноте и качеству ответа"
    "и если ответ не идеальный порекомендовать, как его можно улучить"
)


def evaluate_answer(question: str, answer: str, correct_answer: str, feedback: bool) -> str:
    """
    Функция для оценки ответа пользователя чат-ботом через API
    """
    messages = [
        SystemMessage(
            content=setting_feedback if feedback else setting_evaluate,
        )
    ]
    user_input = (f"вопрос: '{question}' "
                  f"ответ пользователя: '{answer}' "
                  f"правильный ответ для сравнения: '{correct_answer}'")
    messages.append(HumanMessage(content=user_input))
    res = chat.invoke(messages)
    messages.append(res)
    return res.content
