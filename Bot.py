import logging
import random
import time
from datetime import datetime, time
import os
from telegram.ext import Application, CommandHandler
from telegram.error import BadRequest, Forbidden

# Configure logging to use UTC time
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
formatter.converter = time.gmtime
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Get bot token and chat ID from environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

if not BOT_TOKEN or not CHAT_ID:
    logging.error("BOT_TOKEN or CHAT_ID environment variables are not set.")
    exit(1)

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

# Function to send scheduled messages
def send_scheduled_message(context):
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
                context.bot.send_message(chat_id=CHAT_ID, text=full_message)
                logging.info(f"Message sent at {current_time_str} UTC: {full_message}")
                last_sent_dates[target] = current_date
            except BadRequest as e:
                logging.error(f"Bad request error: {e}")
            except Forbidden as e:
                logging.error(f"Forbidden error: {e}. Check bot permissions.")
            except Exception as e:
                logging.error(f"Unexpected error: {e}")

# Handler for /start command
def start(update, context):
    update.message.reply_text("Bot is running and will send messages at scheduled times.")

def main():
    logging.info("Bot is starting")
    # Initialize the Application
    application = Application.builder().token(BOT_TOKEN).build()
    # Add command handler
    application.add_handler(CommandHandler("start", start))
    # Schedule the message sender to run every 30 seconds
    application.job_queue.run_repeating(send_scheduled_message, interval=30, first=0)
    # Start polling
    logging.info("Starting bot polling")
    application.run_polling()

if __name__ == '__main__':
    main()
