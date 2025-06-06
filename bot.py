import asyncio
import random
from datetime import datetime, time
from aiogram import Bot, Dispatcher, types
import os
import pytz
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot with your token and group chat ID from environment variables
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Validate environment variables
if not BOT_TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables. Please set it securely.")
if not CHAT_ID:
    raise ValueError("No TELEGRAM_CHAT_ID found in environment variables. Please set it securely.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# List of 4 different messages
MESSAGES = [
    "Hey team, time for a quick sync! What's the latest?",
    "It's time to check in! Any updates to share?",
    "Hello everyone, let's touch base! What's on your mind?",
    "Time for our daily catch-up! What's new with you all?"
]

# Define scheduled tasks for messages and stickers
# Replace 'sticker1', 'sticker2', etc., with actual Telegram sticker file IDs
scheduled_tasks = [
    {'time': time(13, 0), 'type': 'message'},  # 1:00 PM EAT
    {'time': time(14, 0), 'type': 'message'},  # 2:00 PM EAT
    {'time': time(15, 0), 'type': 'message'},  # 3:00 PM EAT
    {'time': time(16, 0), 'type': 'message'},  # 4:00 PM EAT
    {'time': time(10, 0), 'type': 'sticker', 'sticker_id': 'sticker1'},  # 10:00 AM EAT
    {'time': time(12, 0), 'type': 'sticker', 'sticker_id': 'sticker2'},  # 12:00 PM EAT
    {'time': time(17, 0), 'type': 'sticker', 'sticker_id': 'sticker3'},  # 5:00 PM EAT
    {'time': time(19, 0), 'type': 'sticker', 'sticker_id': 'sticker4'}   # 7:00 PM EAT
]

# Function to send scheduled content (messages or stickers)
async def send_scheduled_content():
    tz = pytz.timezone('Africa/Nairobi')  # EAT timezone
    while True:
        now = datetime.now(tz)
        for task in scheduled_tasks:
            target_time = task['time']
            # Combine with today's date
            target_datetime = datetime.combine(now.date(), target_time, tzinfo=tz)
            # Calculate time difference in seconds
            time_diff = abs((now - target_datetime).total_seconds())
            if time_d⁶7iff < 60:  # Within a 1-minute window
                if task['type'] == 'message':
                    message = random.choice(MESSAGES)
                    full_message = f"[{now.strftime('%H:%M:%S')} EAT] {message}"
                    try:
                        await bot.send_message(chat_id=CHAT_ID, text=full_message)
                        logger.info(f"Message sent: {full_message}")
                    except Exception as e:
                        logger.error(f"Error sending message: {e}")
                elif task['type'] == 'sticker':
                    sticker_id = task['sticker_id']
                    try:
                        await bot.send_sticker(chat_id=CHAT_ID, sticker=sticker_id)
                        logger.info(f"Sticker sent: {sticker_id}")
                    except Exception as e:
                        logger.error(f"Error sending sticker: {e}")
                # Sleep for 60 seconds to avoid multiple sends in the same minute
                await asyncio.sleep(60)
        # Check every 30 seconds
        await asyncio.sleep(30)

# Handler for /start command to confirm bot is running
@dp.message(commands=['start'])
async def start_command(message: types.Message):
    await message.reply(
        "Bot is running and will send messages to the private group at 1:00 PM, 2:00 PM, 3:00 PM, and 4:00 PM EAT, "
        "and stickers at 10:00 AM, 12:00 PM, 5:00 PM, and 7:00 PM EAT daily.")

# Main execution
async def main():
    # Start the scheduled content task
    asyncio.create_task(send_scheduled_content())
    # Start polling
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
