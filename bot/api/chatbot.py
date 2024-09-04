from bot.config_reader import config
import aiohttp

# инструкции для чат-бота
setting_task_evaluate = ("""
Ты — эксперт по Data Science с опытом в оценке качества ответов. Твоя задача — оценить ответ по шкале от 0 до 5, где 0
— неверный, 5 — полностью правильный. Игнорируй орфографию, отвечай только числом.
""")

setting_task_feedback = ("""
Ты — эксперт по Data Science с опытом в анализе данных и машинном обучении. Твоя задача — предоставить конструктивный 
отзыв по качеству и полноте ответа на заданный вопрос. Оцени, насколько ответ является полным и точным, а также 
порекомендуй, как можно улучшить его, если он не идеален. Пожалуйста, сосредоточься на ключевых аспектах, таких как 
правильность представленных данных и логика изложения. Если можно ответить кратко, пожалуйста, сделай это. Используй 
дружелюбный тон, обращаясь на 'ты'. Игнорируй орфографические ошибки и сосредоточься на содержательном анализе. Отвечай 
в формате markdown
""")


setting_algo_evaluate = ("""
Ты оцениваешь решение алгоритмической задачки на python. Твоя задача - принять решение или нет. Если код работает, то
напиши "Принято", если в коде ошибки, то "Не принято". Отвечай только Принято или Не принято"
""")

setting_algo_feedback = ("""
Ты оцениваешь решение алгоритмической задачи на Python. Твоя задача — кратко указать на ошибки и предложить, где можно 
оптимизировать код. Не предоставляй полный код, только конкретные советы по улучшению. Если код оптимален, напиши: 
"Код оптимален". Если есть ошибки или возможные улучшения, укажи их кратко и по существу. Отвечай в формате markdown
""")


async def evaluate_answer(setting: str, **kwargs) -> str:
    setting_dict = {
        'task_evaluate': setting_task_evaluate,
        'task_feedback': setting_task_feedback,
        'algo_evaluate': setting_algo_evaluate,
        'algo_feedback': setting_algo_feedback
    }
    setting = setting_dict.get(setting)

    if setting in ['task_evaluate', 'task_feedback']:

        question_info = (f"Вопрос для анализа: '{kwargs['question']}'\n"
                         f"Информация по вопросу для оценки: '{kwargs['correct_answer']}'")

        user_input = f"Ответ, который нужно оценить: {kwargs['answer']}"

    else:

        question_info = f"Вот задание: '{kwargs['question']}'\n"
        user_input = f"Код, который нужно оценить: {kwargs['answer']}"

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
