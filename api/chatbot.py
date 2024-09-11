from config_reader import config
import aiohttp

# инструкции для чат-бота
setting_task_evaluate = ("""
Ты — эксперт по Data Science с опытом в оценке качества ответов. Твоя задача — оценить ответ по шкале от 0 до 5, где 0
— неверный, 5 — полностью правильный. Игнорируй орфографию, отвечай только числом.
""")

# setting_task_feedback = ("""
# Ты — эксперт по Data Science с опытом в анализе данных и машинном обучении. Твоя задача — предоставить конструктивный
# отзыв по качеству и полноте ответа на заданный вопрос. Оцени, насколько ответ является полным и точным, а также
# порекомендуй, как можно улучшить его, если он не идеален. Пожалуйста, сосредоточься на ключевых аспектах, таких как
# правильность представленных данных и логика изложения. Если можно ответить кратко, пожалуйста, сделай это. Используй
# дружелюбный тон, обращаясь на 'ты'. Игнорируй орфографические ошибки и сосредоточься на содержательном анализе.
# Отвечай в формате markdown telegram
# """)


setting_task_feedback = ("""
Ты — эксперт по Data Science. Твоя задача — дать отзыв на ответ. Оцени полноту, точность и предложи улучшения. 
Фокусируйся на правильности данных и логике. Отвечай кратко, если это возможно, и дружелюбно. Игнорируй орфографию, анализируй содержание. 
Формат — markdown telegram.
""")

setting_algo_evaluate = ("""
Ты оцениваешь решение алгоритмической задачки на python. Твоя задача - принять решение или нет. Если код работает, то
напиши "Принято", если в коде ошибки, то "Не принято". Отвечай только Принято или Не принято"
""")

setting_algo_feedback = ("""
Ты оцениваешь решение алгоритмической задачи на Python. Твоя задача — кратко указать на ошибки и предложить, где можно 
оптимизировать код. Не предоставляй полный код, только конкретные советы по улучшению. Если код оптимален, напиши: 
"Код оптимален". Если есть ошибки или возможные улучшения, укажи их кратко и по существу. 
Отвечай в формате markdown telegram
""")

setting_interview = ("""
Твоя задача — выступать в роли HR-специалиста, который проводит техническое собеседование на 
позицию Data Scientist. Придумай себе имя и название компании и используй их в письме. Твоя цель — на основе анализа 
12 ответов кандидата принять одно из двух решений: 1. Предложить офер на работу только в том случае, если все или 
почти все ответы кандидата соответствуют уровню позиции (test_level). Предложение офера возможно только при высоком 
соответствии ответов с ожидаемым уровнем знаний. Учти, что даже небольшие ошибки могут стать причиной отказа на 
младших уровнях. 2. Если ответы кандидата не соответствуют ожидаемому уровню, предложи отказ. Даже при наличии 
нескольких неправильных или неполных ответов — откажи в офере, четко объяснив, что именно необходимо улучшить для 
будущего успеха. Важно: • Первой строкой всегда идет фраза: “Собеседование на уровень {test_level}”, где test_level 
может быть junior, middle, senior или team lead. • Далее идут 12 вопросов и ответов кандидата. • Оцени ответы 
кандидата с особым вниманием на точность и полноту. • Junior: Офер предлагается только при высокой точности 
большинства ответов. Допускаются только мелкие ошибки, но не в ключевых областях. • Middle: Кандидат должен давать 
полные и точные ответы, допускается 1-2 незначительные неточности. • Senior: Ответы должны быть почти безупречными, 
даже мелкие ошибки могут привести к отказу. • Team Lead: Любые ошибки или неточности — недопустимы. • Убедись, 
что зарплата точно изменяется в зависимости от качества ответов. Например: • Для junior: 105 тыс. рублей для средних 
ответов, 130 тыс. рублей для отличных. • Для senior: 280 тыс. рублей для хороших ответов, 350 тыс. рублей для 
отличных. Офер дается только при полном соответствии ожиданиям, в офере указывается конкретная заработная плата 
в зависимости от качества ответов.
""")


async def evaluate_answer(setting: str, **kwargs) -> str:
    """
    Универсальная функция для общения с yandex gpt
    """
    setting_dict = {
        'task_evaluate': setting_task_evaluate,
        'task_feedback': setting_task_feedback,
        'algo_evaluate': setting_algo_evaluate,
        'algo_feedback': setting_algo_feedback,
        'interview_offer': setting_interview
    }

    if setting in ['task_evaluate', 'task_feedback']:

        question_info = (f"Вопрос для анализа: '{kwargs['question']}'\n"
                         f"Информация по вопросу для оценки: '{kwargs['correct_answer']}'")
        user_input = f"Ответ, который нужно оценить: {kwargs['answer']}"
        temperature = 0.1

    elif setting in ['algo_evaluate', 'algo_feedback']:

        question_info = f"Вот задание: '{kwargs['question']}'\n"
        user_input = f"Код, который нужно оценить: {kwargs['answer']}"
        temperature = 0

    else:
        question_info = ''
        user_input = kwargs['user_input']
        temperature = 1

    setting = setting_dict.get(setting)

    prompt = {
        "modelUri": f"gpt://{config.FOLDER_ID.get_secret_value()}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": temperature,
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
