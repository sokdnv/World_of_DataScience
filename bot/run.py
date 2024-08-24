from aiogram import Bot, Dispatcher
import logging
import asyncio

from app.command_handlers import router

from bot.util.config import TOKEN

# сам бот
bot = Bot(token=TOKEN)
# штука для обработки событий
dp = Dispatcher()


async def main():
    # тащим хэндлеры из скрипта с роутером
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('exit')
