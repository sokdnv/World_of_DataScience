from aiogram import Bot, Dispatcher
import logging
import asyncio
from aiogram.client.default import DefaultBotProperties

from app.command_handlers import router

from bot.util.config import TOKEN

# сам бот
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='Markdown'))
# штука для обработки событий
dp = Dispatcher()


async def main():
    # тащим хэндлеры из скрипта с роутером
    dp.include_router(router)
    # удаляем фигню, которая приходила пока бот не работал
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('exit')
