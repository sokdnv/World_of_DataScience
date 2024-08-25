from aiogram import Bot, Dispatcher
import asyncio
from aiogram.client.default import DefaultBotProperties

import logging

from bot.handlers import commands, tests

from bot.config_reader import config


async def main():
    # сам бот
    bot = Bot(token=config.BOT_TOKEN.get_secret_value(), default=DefaultBotProperties(parse_mode='Markdown'))
    # штука для обработки событий
    dp = Dispatcher()
    # тащим роутеры из хэнледров
    dp.include_routers(
        commands.router,
        tests.router
    )
    # удаляем фигню, которая приходила пока бот не работал
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('exit')
