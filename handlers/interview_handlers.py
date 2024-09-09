from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext

from funcs.vars import users
from funcs.load_funcs import load_check
import keyboards.inline as kb_i
from handlers.user_state import UserState

# роутер для передачи хэндлеров в основной скрипт
router = Router()


@router.callback_query(F.data == 'interview')
async def start_interview(callback_query: CallbackQuery, state: FSMContext):
    """
    Хэндлер колбэка 'interview'
    """
    user_id = callback_query.from_user.id
    await load_check(user_id)
    await state.update_data(message_id=callback_query.message.message_id)

    current_level = await users[user_id].get_current_level()
    if current_level < 20:
        text = f"```Interview\nYou need {20 - current_level} more levels to try this mode```"
        await callback_query.message.edit_text(text, reply_markup=kb_i.to_menu_kb)

    else:
        _, _, grade = await users[user_id].calculate_levels()
        text = (f"```Interview\nПроверь свои навыки в режиме интервью уровня {grade}!\n"
                f"Ответь на 12 вопросов подряд, но имей в виду: если переключишься на другую задачу,"
                f" твой прогресс будет потерян.\n"
                f"Убедись, что в твоем распоряжении достаточно времени, и начинай, когда будешь готов!\n"
                f"Важно: в этом режиме нет возможности пропустить вопрос, тебе придется что-то написать на каждый!```")
        await callback_query.message.edit_text(text, reply_markup=kb_i.enter_interview_kb)


@router.callback_query(F.data == 'start_interview')
async def interview(callback_query: CallbackQuery, state: FSMContext):
    """
    Хэндлер начала интервью
    """
    user_id = callback_query.from_user.id
    data = await state.get_data()
    await callback_query.bot.delete_message(chat_id=user_id,
                                            message_id=data['message_id'])
    await users[user_id].start_interview()
    await state.set_state(UserState.interview)
    await state.update_data(user_id=user_id)
    await ask_question(callback_query.message, state)


async def ask_question(message: Message, state: FSMContext):
    """
    Функция, тянущая вопрос из интервью
    """
    data = await state.get_data()
    user_id = data['user_id']
    question, _ = await users[user_id].test.ask_question()

    if not question:
        text = (f"```Interview\nВаше собеседование завершено! "
                f"Мы свяжемся с вами в ближайшее время, чтобы сообщить решение. "
                f"Спасибо за ваше время и терпение.```")
        await state.clear()
        await message.answer(text, reply_markup=kb_i.to_menu_kb)

        # TODO Дописать под отправку pdf с офером
        offer = await users[user_id].test.give_offer()
        await message.answer_document(BufferedInputFile(file=offer.read(), filename='offer.pdf'),
                                      reply_markup=kb_i.offer_kb)
    else:
        await message.answer(text=question)


@router.message(UserState.interview)
async def process_answer(message: Message, state: FSMContext):
    """
    Хэндлер обрабатывающий ответ на интервью
    """
    user_id = message.from_user.id
    users[user_id].test.get_answer(answer=message.text)
    await ask_question(message, state)


@router.callback_query(F.data == "delete_message")
async def delete_message(callback_query: CallbackQuery):
    """
    Хэндлер для удаления сообщения
    """
    await callback_query.message.delete()

