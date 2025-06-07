import asyncio
import random
from datetime import datetime, time
from aiogram import Bot, Dispatcher, types
from aiogram import filters
import pytz
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace these with your actual bot token and chat ID
BOT_TOKEN = '7840823330:AAE38cSg08GppMDW9HCBso0SXIADaYfvfDE'
CHAT_ID = '-1002621381308'

# Check if placeholders are still present
if BOT_TOKEN == 'your_bot_token_here':
    raise ValueError("Please replace 'your_bot_token_here' with your actual bot token.")
if CHAT_ID == 'your_chat_id_here':
    raise ValueError("Please replace 'your_chat_id_here' with your actual chat ID.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# List of 4 different messages
MESSAGES = [
    "Hey team, time for a quick sync! What's the latest?",
    "It's time to check in! Any updates to share?",
    "Hello everyone, let's touch base! What's on your mind?",
    "Time for our daily catch-up! What's new with you all?"
]

# Function to send messages at scheduled times
async def send_scheduled_message():
    tz = pytz.timezone('Africa/Addis_Ababa')  # EAT timezone for Ethiopia
    while True:
        current_dt = datetime.now(tz)
        logger.info(f"Current datetime: {current_dt}")
        # Define target times (in EAT)
        target_times = [
            time(19, 0),  # 7:00 PM
            time(20, 0),  # 8:00 PM
            time(21, 0),  # 9:00 PM
            time(22, 37)   # 10:00 PM (corrected from 22:30)
        ]

        for target in target_times:
            target_dt = datetime.combine(current_dt.date(), target, tzinfo=tz)
            time_diff = abs((current_dt - target_dt).total_seconds())
            # Log details for debugging
            logger.info(f"Target: {target}, target_dt: {target_dt}, current_dt: {current_dt}, time_diff: {time_diff}")
            if time_diff < 60:
                logger.info(f"Scheduled time detected: {target}")
                current_time = current_dt.strftime("%H:%M:%S")
                message = random.choice(MESSAGES)
                full_message = f"[{current_time} EAT] {message}"
                try:
                    await bot.send_message(chat_id=CHAT_ID, text=full_message)
                    logger.info(f"Message sent to group at {current_time}: {full_message}")
                except Exception as e:
                    logger.error(f"Error sending message to group: {e}")
                # Wait 60 seconds to avoid sending multiple messages in the same minute
                await asyncio.sleep(60)

        # Check every 10 seconds to avoid missing the target time
        await asyncio.sleep(10)

# Handler for /start command to confirm bot is running
@dp.message(filters.Command("start"))
async def start_command(message: types.Message):
    await message.reply(
        "Bot is running and will send messages to the private group at 7:00 PM, 8:00 PM, 9:00 PM, and 10:00 PM EAT daily."
    )

# Main execution
async def main():
    # Test message to verify permissions
    try:
        await bot.send_message(CHAT_ID, "Bot started successfully. This is a test message to verify permissions.")
        logger.info("Test message sent successfully.")
    except Exception as e:
        logger.error(f"Error sending test message: {e}")

    # Start the scheduled message task
    asyncio.create_task(send_scheduled_message())
    # Start polling
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
