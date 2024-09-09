# World of Data Science - Telegram RPG Bot

## Описание проекта


**World of Data Science** — это Telegram-бот, который превращает обучение Data Science и алгоритмам в захватывающее RPG-приключение! 🎮 Здесь ты сможешь не только улучшить свои навыки в программировании, машинном обучении и аналитике данных, но и погружаться в игровой процесс, прокачивая своего персонажа.

Бот предлагает несколько увлекательных режимов тестирования: от напряжённых блиц-викторин на время до работы над ошибками, а также алгоритмические задачки, которые тебе предстоит решать с помощью кода. По мере прохождения ты будешь повышать уровень в таких областях, как Python, алгоритмы, SQL, машинное и глубокое обучение, и математика. И конечно, не забывай про достижения и ранги — чем больше ты учишься, тем ближе становишься к вершинам Data Science! 🌟

## Основные возможности

- **Тестирование**: 
  - **Basic Test** — стандартные вопросы по Data Science.
  - **Blitz Test** — вопросы с ограничением по времени.
  - **Mistake Test** — работа над ошибками.
  
- **Алгоритмические задачи**: 
  - Решение задач с отправкой кода на проверку.

- **Уровни и достижения**:
  - Прокачивай навыки в 6 ключевых областях: Python, алгоритмы, SQL, машинное обучение (ML), глубокое обучение (DL) и математика.
  - Система рангов и достижений на основе выполненных задач и тестов.
  
- **Новости и вакансии**:
  - Получение свежих новостей и вакансий в мире Data Science.

## Структура проекта

```plaintext
pocket_mentor/
│
├── api/                  # Взаимодействие с API
├── classes/              # Классы для работы с пользователями, тестами и задачами
├── funcs/                # Вспомогательные функции, работа с базой данных
├── handlers/             # Обработчики команд и callback'ов
├── image_gen/            # Вспомогательные файлы для генерации изображений
├── keyboards/            # Функции для создания inline-клавиатур Telegram
├── texts/                # Текстовые сообщения, используемые ботом (приветствия, обучающие тексты)
│
├── config_reader.py      # Конфигурация для работы с внешними API и БД
├── requirements.txt      # Список зависимостей
└── run.py                # Основной скрипт для запуска бота
```

## Используемые технологии

- **Python 3.11**
- **Aiogram** — библиотека для создания ботов в Telegram.
- **Motor** — асинхронный драйвер для работы с MongoDB.
- **Pillow** — библиотека для обработки изображений.
- **Yandex GPT** — LLM для оценки и фидбэка по задачам
