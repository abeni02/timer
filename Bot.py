import telegram
import schedule
import time
from datetime import datetime
import logging

# Configure logging to track bot activity and errors
logging.basicConfig(filename='bot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Replace these placeholders with your actual values
API_TOKEN = "your_api_token_here"  # Your Telegram bot's API token
bot = telegram.Bot(token=API_TOKEN)
group_chat_id = "your_group_chat_id_here"  # Your Telegram group chat ID

# Define the times and corresponding stickers
schedule_times = ["13:00", "14:00", "15:00", "16:00", "17:00"]
time_strs = ["1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM"]
stickers = [
    "your_sticker_file_id_for_1pm_here",
    "your_sticker_file_id_for_2pm_here",
    "your_sticker_file_id_for_3pm_here",
    "your_sticker_file_id_for_4pm_here",
    "your_sticker_file_id_for_5pm_here"
]

# Function to send a message and sticker at specified times
def send_message(time_str, sticker_file_id):
    try:
        bot.send_message(chat_id=group_chat_id, text=f"It's {time_str}")
        logging.info(f"Sent message: It's {time_str}")
        bot.send_sticker(chat_id=group_chat_id, sticker=sticker_file_id)
        logging.info(f"Sent sticker: {sticker_file_id}")
    except Exception as e:
        logging.error(f"Error in send_message: {str(e)}")

# Function to send the current server time every minute
def send_server_time():
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bot.send_message(chat_id=group_chat_id, text=f"Server time: {current_time}")
        logging.info(f"Sent server time: {current_time}")
    except Exception as e:
        logging.error(f"Error in send_server_time: {str(e)}")

# Schedule messages at specified times with corresponding stickers
for sch_time, time_str, sticker in zip(schedule_times, time_strs, stickers):
    schedule.every().day.at(sch_time).do(send_message, time_str, sticker)

# Schedule server time every minute
schedule.every(1).minutes.do(send_server_time)

# Keep the script running to execute scheduled tasks
while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception as e:
        logging.error(f"Error in main loop: {str(e)}")
        time.sleep(1)  # Prevent tight loop on failure
