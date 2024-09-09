from funcs.database import question_collection
from motor.motor_asyncio import AsyncIOMotorCollection
from classes.tester import ask_question
from api.chatbot import evaluate_answer


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import mm

import io


def create_pdf(text: str) -> io.BytesIO:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    yellow = (0.835, 0.937, 0.306)
    grey = (0.118, 0.118, 0.118)

    pdfmetrics.registerFont(
        TTFont('Times-Roman', 'image_gen/int_font.ttf'))

    c.setFont("Times-Roman", 12)

    c.setFillColor(grey)
    c.rect(0, 0, A4[0], A4[1], fill=1)

    c.setFillColor(yellow)

    width, height = A4
    text_object = c.beginText(40 * mm, height - 40 * mm)

    max_width = width - 80 * mm

    lines = text.split('\n')
    for line in lines:
        words = line.split(' ')
        wrapped_line = ''
        for word in words:
            if c.stringWidth(wrapped_line + word, "Times-Roman", 12) <= max_width:
                wrapped_line += word + ' '
            else:
                text_object.textLine(wrapped_line.strip())
                wrapped_line = word + ' '

        if wrapped_line:
            text_object.textLine(wrapped_line.strip())
        text_object.textLine('')

    c.drawText(text_object)

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer


async def generate_interview(level: str,
                             db: AsyncIOMotorCollection = question_collection) -> list:
    """
    Функция для генерации вопросов на основе уровня сложности.
    Уровень сложности: junior, middle, senior, team_lead.
    Вопросы выбираются из шести категорий, по 2 вопроса из каждой категории.
    """

    difficulty_mapping = {
        "junior": (2, 3),
        "middle": (3, 4),
        "senior": (4, 5),
        "team_lead": (5, 5)
    }

    difficulties = difficulty_mapping[level]
    categories = ['python', 'algorithms', 'math', 'SQL', 'ML', 'DL']

    questions = []

    for category in categories:
        for difficulty in difficulties:
            match_stage = {
                "$match": {
                    "category": category,
                    "difficulty": difficulty
                }
            }

            pipeline = [
                match_stage,
                {"$sample": {"size": 1}}
            ]

            question_cursor = db.aggregate(pipeline)
            question = await question_cursor.to_list(length=1)
            questions.append(question[0])

    return questions


class InterviewTest:
    """
    Класс эмуляции собеседования
    """

    def __init__(self, test_level: str, user_name: str) -> None:
        self.interview_log = [f'Имя соискателя: {user_name}\nСобеседование на уровень {test_level}']
        self.test_level = test_level
        self.questions = None
        self.question_index = 0

    async def generate_questions(self) -> None:
        """
        Метод для создания вопросов для собеседования
        """
        self.questions = await generate_interview(self.test_level)

    async def ask_question(self) -> tuple[str, str] | tuple[None, None]:
        """
        Метод для отправки вопроса и добавления его в лог
        """
        if not self.questions:
            await self.generate_questions()

        if self.question_index == 1:
            return None, None

        current_question = self.questions[self.question_index]
        self.question_index += 1
        self.interview_log.append('Вопрос: ' + current_question['question'])

        return ask_question(current_question)

    def get_answer(self, answer: str) -> None:
        """
        Метод для добавления ответа в лог
        """
        self.interview_log.append('Ответ: ' + answer)

    async def give_offer(self) -> io.BytesIO:
        """
        Метод для отправки офера
        """
        user_input = '\n'.join(self.interview_log)
        bot_answer = await evaluate_answer(setting='interview_offer', user_input=user_input)
        pdf_buffer = create_pdf(bot_answer)
        return pdf_buffer
