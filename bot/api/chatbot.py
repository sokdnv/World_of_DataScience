from bot.config_reader import config
from langchain_community.chat_models.gigachat import GigaChat
from langchain.schema import HumanMessage, SystemMessage
import requests
import json


chat = GigaChat(credentials=config.CHAT_API.get_secret_value(),
                verify_ssl_certs=False)

# инструкции для чат-бота
setting_evaluate = ("""
Ты являешься экспертом по Data Science с многолетним опытом в оценке качества ответов на 
вопросы. Тебя ценят за твой тщательный анализ и объективный подход к оценке, что делает тебя надежным источником для 
определения правильности и полноты информации. Твоя задача — оценить качество ответа на заданный вопрос. Пожалуйста, 
используй шкалу от 0 до 5, где 0 означает абсолютно неверный ответ, а 5 — полностью правильный и исчерпывающий ответ. 
Игнорируй орфографические ошибки и не давай никаких объяснений. Просто ответь одним числом. Пустой ответ оценивается 
как 0
""")

setting_feedback = ("""
Ты являешься экспертом в области Data Science с многолетним опытом работы и глубокой 
экспертизой в анализе данных и машинном обучении. Твоя задача — предоставить конструктивный отзыв по качеству и 
полноте ответа на заданный вопрос. Оцени, насколько ответ является полным и точным, а также порекомендуй, 
как можно улучшить его, если он не идеален. Пожалуйста, сосредоточься на ключевых аспектах, таких как правильность 
представленных данных и логика изложения. Если можно ответить кратко, пожалуйста, сделай это. Используй дружелюбный 
тон, обращаясь на 'ты'. Игнорируй орфографические ошибки и сосредоточься на содержательном анализе. 
""")


def evaluate_answer(question: str, answer: str, correct_answer: str, feedback: bool) -> str:
    """
    Функция для оценки ответа пользователя чат-ботом через API
    """
    messages = [
        SystemMessage(
            content=setting_feedback if feedback else setting_evaluate,
        )
    ]

    user_input = (f"Вот вопрос для анализа: '{question}' "
                  f"Вот ответ, который нужно оценить: '{answer}' "
                  f"Пример правильного ответа для сравнения:: '{correct_answer}'")

    messages.append(HumanMessage(content=user_input))
    res = chat.invoke(messages)
    messages.append(res)
    return res.content


def evaluate_answer_ya(question: str, answer: str, correct_answer: str, feedback: bool) -> str:

    setting = setting_feedback if feedback else setting_evaluate

    user_input = (f"Вот вопрос для анализа: '{question}'\n"
                  f"Пример правильного ответа для сравнения:: '{correct_answer}'\n"
                  f"Вот ответ, который нужно оценить: '{answer}'")

    prompt = {
        "modelUri": f"gpt://{config.FOLDER_ID.get_secret_value()}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.1,
            "maxTokens": "300"
        },
        "messages": [
            {
                "role": "user",
                "text": setting + user_input
            }
        ]
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {config.YANDEX_API_KEY.get_secret_value()}"
    }

    response = requests.post(url, headers=headers, json=prompt)
    result = json.loads(response.text)
    answer = result['result']['alternatives'][0]['message']['text']

    return answer
