import os
import logging
from datetime import datetime
import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.exceptions import TelegramUnauthorizedError, TelegramBadRequest, TelegramNetworkError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
TARGET_GROUP_ID = os.getenv('TARGET_GROUP_ID')

# Validate environment variables
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in the .env file")
if not TARGET_GROUP_ID:
    raise ValueError("TARGET_GROUP_ID is not set in the .env file")
try:
    TARGET_GROUP_ID = int(TARGET_GROUP_ID)
except ValueError:
    raise ValueError("TARGET_GROUP_ID must be an integer")

# Debug: Log loaded environment variables
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logger.info(f"Loaded BOT_TOKEN: {BOT_TOKEN}")
logger.info(f"Loaded TARGET_GROUP_ID: {TARGET_GROUP_ID}")

# Define sticker IDs for each time slot
# IMPORTANT: Replace placeholders with actual sticker file IDs from @GetIDsBot
sticker_ids = {
    '13:00': 'AAMCBQADGQEAATX4LmhBi6HI38gfxgvirSsB1zBxBkgMAALCBAACDziZV7tOfQfd_g3NAQAHbQADNgQ',  # e.g., 'CAACAgIAAxkBAAIB...'
    '14:00': 'AAMCBQADGQEAATX4MmhBi7gT5uHYCjpoOdDCGDRzTW5zAAJ1BwAC1I6YV-cenhZ8_IX7AQAHbQADNgQ',
    '15:00': 'AAMCBQADGQEAATX4PGhBi-I36ExMXphcyO_6KxU33vV_AAK7BAACKEyRV7KSqggTKA7zAQAHbQADNgQ',
    '16:00': 'AAMCBQADGQEAATX4QGhBi_3k74-8X0DXaQPh6fKtXsC_AAIWBQACAW-YVwIlsmmYzIcWAQAHbQADNgQ',
    '17:00': 'AAMCBQADGQEAATX4QmhBjCRvIHxDUjP6LYksV3dOQX8ZAAKrBQACTDWQV6HZhG2dpSWFAQAHbQADNgQ',
}

# Define scheduled times in EAT (24-hour format)
scheduled_times = ['13:00', '14:00', '15:00', '16:00', '17:00']

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Add handler to ignore unhandled updates
router = Router()
dp.include_router(router)

@router.message()
async def ignore_messages(message):
    pass  # Silently ignore all unhandled messages to reduce log clutter

# Asynchronous function to validate bot token
async def validate_bot_token():
    """Validate the bot token by making a test API call."""
    try:
        bot_info = await bot.get_me()
        logger.info(f"Bot validated successfully: @{bot_info.username} (ID: {bot_info.id})")
        return True
    except TelegramUnauthorizedError as e:
        logger.error(f"Invalid BOT_TOKEN: {e}. Please check the BOT_TOKEN in your .env file.")
        return False
    except Exception as e:
        logger.error(f"Error validating bot token: {e}")
        return False

# Asynchronous function to send scheduled message and sticker
async def send_scheduled_message(time_str: str):
    """Send a scheduled message and corresponding sticker to the private group."""
    message = f"Good afternoon! Here's your {time_str} update."
    sticker_id = sticker_ids[time_str]
    try:
        await bot.send_message(chat_id=TARGET_GROUP_ID, text=message)
        await bot.send_sticker(chat_id=TARGET_GROUP_ID, sticker=sticker_id)
        logger.info(f"Message and sticker sent for {time_str} EAT")
    except TelegramUnauthorizedError as e:
        logger.error(f"Unauthorized error sending message/sticker for {time_str}: {e}. Check BOT_TOKEN.")
    except TelegramBadRequest as e:
        logger.error(f"Bad request error sending message/sticker for {time_str}: {e}. Check TARGET_GROUP_ID or sticker IDs.")
    except TelegramNetworkError as e:
        logger.error(f"Network error sending message/sticker for {time_str}: {e}. Check internet connection.")
    except Exception as e:
        logger.error(f"Unexpected error sending message/sticker for {time_str}: {e}")

# Asynchronous function to log deployment server time every minute
async def log_server_time():
    """Log the current deployment server time internally every minute."""
    now = datetime.now()
    logger.info(f"{now} - Deployment Server Time Update")

async def main():
    # Validate bot token before proceeding
    if not await validate_bot_token():
        logger.error("Bot token validation failed. Exiting.")
        return

    # Initialize scheduler with EAT timezone (UTC+3)
    scheduler = AsyncIOScheduler(timezone='Africa/Addis_Ababa')

    # Schedule daily messages for each time slot
    for time_str in scheduled_times:
        hour, minute = map(int, time_str.split(':'))
        scheduler.add_job(
            send_scheduled_message,
            'cron',
            hour=hour,
            minute=minute,
            args=[time_str],
            misfire_grace_time=60  # Allow 60 seconds grace time for missed jobs
        )

    # Schedule server time logging every minute
    scheduler.add_job(
        log_server_time,
        'interval',
        minutes=1,
        misfire_grace_time=30  # Allow 30 seconds grace time
    )

    # Start the scheduler
    scheduler.start()
    logger.info("Scheduler started with jobs for EAT messages and deployment server time logging")

    # Start the bot polling
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error during polling: {e}")

if __name__ == '__main__':
    asyncio.run(main())

