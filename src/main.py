import asyncio
import logging

from aiogram import Bot, Dispatcher

from src.bot.handlers import router
from src.config import settings
from src.db.engine import init_db
from src.db.loader import load_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def on_startup() -> None:
    logger.info("Инициализация БД...")
    await init_db()
    logger.info("Загрузка данных...")
    await load_data()
    logger.info("Бот готов к работе")


async def main() -> None:
    await on_startup()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    dp.include_router(router)

    logger.info("Запуск polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
