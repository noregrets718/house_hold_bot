"""Bot entry point."""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings
from app import db
from app.middlewares.admin import AdminMiddleware
from app.handlers import donors, payments, reports


async def main():
    """Start the bot."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
    logger = logging.getLogger(__name__)

    # Initialize database pool
    logger.info("Connecting to database...")
    await db.create_pool()
    logger.info("Database connected.")

    # Initialize bot
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # Initialize dispatcher
    dp = Dispatcher()

    # Register middleware
    dp.message.middleware(AdminMiddleware())

    # Register routers
    dp.include_router(reports.router)  # /start, /help, /paid, /unpaid, /history, /delete
    dp.include_router(donors.router)   # /add_donor, /remove_donor, /donors
    dp.include_router(payments.router) # plain message payment recording

    try:
        logger.info("Starting bot...")
        await dp.start_polling(bot)
    finally:
        logger.info("Shutting down...")
        await db.close_pool()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
