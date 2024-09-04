from bot.config_reader import config
import aiohttp

# инструкции для чат-бота
setting_evaluate = ("""
Ты — эксперт по Data Science с опытом в оценке качества ответов. Твоя задача — оценить ответ по шкале от 0 до 5, где 0
— неверный, 5 — полностью правильный. Игнорируй орфографию, отвечай только числом.
""")

# setting_evaluate = ("""
# Ты являешься экспертом по Data Science с многолетним опытом в оценке качества ответов на
# вопросы. Тебя ценят за твой тщательный анализ и объективный подход к оценке, что делает тебя надежным источником для
# определения правильности и полноты информации. Твоя задача — оценить качество ответа на заданный вопрос. Пожалуйста,
# используй шкалу от 0 до 5, где 0 означает абсолютно неверный ответ, а 5 — полностью правильный и исчерпывающий ответ.
# Игнорируй орфографические ошибки и не давай никаких объяснений. Просто ответь одним числом.
# """)

# setting_feedback = ("""
# Ты — эксперт по Data Science с опытом в анализе данных и машинном обучении. Твоя задача — дать отзыв о качестве и
# полноте ответа, указать, насколько он точен и полон, и предложить улучшения. Сосредоточься на правильности данных и
# логике. Если возможно, отвечай кратко и дружелюбно, игнорируя орфографию.
# """)

setting_feedback = ("""
Ты являешься экспертом в области Data Science с многолетним опытом работы и глубокой
экспертизой в анализе данных и машинном обучении. Твоя задача — предоставить конструктивный отзыв по качеству и
полноте ответа на заданный вопрос. Оцени, насколько ответ является полным и точным, а также порекомендуй,
как можно улучшить его, если он не идеален. Пожалуйста, сосредоточься на ключевых аспектах, таких как правильность
представленных данных и логика изложения. Если можно ответить кратко, пожалуйста, сделай это. Используй дружелюбный
тон, обращаясь на 'ты'. Игнорируй орфографические ошибки и сосредоточься на содержательном анализе.
""")


async def evaluate_answer_ya(question: str, answer: str, correct_answer: str, feedback: bool) -> str:
    setting = setting_feedback if feedback else setting_evaluate

    question_info = (f"Вопрос для анализа: '{question}'\n"
                     f"Информация по вопросу для оценки: '{correct_answer}'")

    user_input = f'Ответ, который нужно оценить: {answer}'

    prompt = {
        "modelUri": f"gpt://{config.FOLDER_ID.get_secret_value()}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.2,
            "maxTokens": "300"
        },
        "messages": [
            {
                "role": "system",
                "text": setting + question_info
            },
            {
                "role": "user",
                "text": user_input
            }
        ]
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {config.YANDEX_API_KEY.get_secret_value()}"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=prompt) as response:
            result = await response.json()
            answer = result['result']['alternatives'][0]['message']['text']
            return answer
