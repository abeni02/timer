import asyncio
import random
import logging
import time
from datetime import datetime, time
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

# Configure logging to use UTC time
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
formatter.converter = time.gmtime  # Use UTC time

# Create a console handler
handler = logging.StreamHandler()
handler.setFormatter(formatter)

# Set up the root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Get bot token and chat ID from environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# Check if environment variables are set
if not BOT_TOKEN or not CHAT_ID:
    logging.error("BOT_TOKEN or CHAT_ID environment variables are not set.")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# List of 4 different messages
MESSAGES = [
    "Hey team, time for a quick sync! What's the latest?",
    "It's time to check in! Any updates to share?",
    "Hello everyone, let's touch base! What's on your mind?",
    "Time for our daily catch-up! What's new with you all?"
]

# Define target times in UTC
target_times = [
    time(9, 21),   # 12:21 PM EAT = 9:21 AM UTC
    time(8, 17),   # 11:17 AM EAT = 8:17 AM UTC
    time(8, 18),   # 11:18 AM EAT = 8:18 AM UTC
    time(8, 19),   # 11:19 AM EAT = 8:19 AM UTC
    time(11, 30)   # 2:30 PM EAT = 11:30 AM UTC (for testing)
]

# Track last sent dates for each target time
last_sent_dates = {target: None for target in target_times}

# Function to calculate seconds since midnight
def seconds_since_midnight(t):
    return t.hour * 3600 + t.minute * 60 + t.second

# Function to send messages at scheduled times
async def send_scheduled_message():
    while True:
        now = datetime.utcnow()
        current_date = now.date()
        current_time = now.time()
        current_seconds = seconds_since_midnight(current_time)

        for target in target_times:
            target_seconds = seconds_since_midnight(target)
            time_diff = abs(current_seconds - target_seconds)
            if time_diff < 60 and (last_sent_dates[target] is None or last_sent_dates[target] < current_date):
                current_time_str = now.strftime("%H:%M:%S")
                message = random.choice(MESSAGES)
                full_message = f"[{current_time_str} UTC] {message}"
                try:
                    await bot.send_message(chat_id=CHAT_ID, text=full_message)
                    logging.info(f"Message sent at {current_time_str} UTC: {full_message}")
                    last_sent_dates[target] = current_date
                except TelegramBadRequest as e:
                    logging.error(f"Bad request error: {e}")
                except TelegramForbiddenError as e:
                    logging.error(f"Forbidden error: {e}. Check bot permissions.")
                except Exception as e:
                    logging.error(f"Unexpected error: {e}")
                await asyncio.sleep(60)  # Wait to avoid multiple sends

        await asyncio.sleep(30)  # Check every 30 seconds

# Handler for /start command
@dp.message(Command('start'))
async def start_command(message: types.Message):
    await message.reply("Bot is running and will send messages at scheduled times.")

# Main execution
async def main():
    logging.info("Starting scheduled message task")
    asyncio.create_task(send_scheduled_message())
    logging.info("Starting bot polling")
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.info("Bot is starting")
    asyncio.run(main())
