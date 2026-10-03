import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from bot_admin_hub import handle_telegram_command

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_CHAT_ID") or os.getenv("ADMIN_ID")

def is_authorized(update: Update) -> bool:
    if not ADMIN_ID:
        return True
    return str(update.effective_user.id) == str(ADMIN_ID)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("⛔ Unauthorized access.")
        return
    await update.message.reply_text(
        "⚡ Alpha Hunter Hub Controller Active

"
        "Commands:
"
        "• /add_drop <Project> <Testnet|Mainnet> <Status> <Task> <Score> <EstVal> <URL>
"
        "• /drops - List tracked campaigns
"
        "• /status - Health check"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    await update.message.reply_text("🟢 All Systems Operational: Alpha Hub Engine & Vercel Feed Ready.")

async def airdrop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("⛔ Unauthorized.")
        return
    raw_text = update.message.text
    response = handle_telegram_command(raw_text, is_admin=True)
    await update.message.reply_text(response)

def main():
    if not BOT_TOKEN:
        print("❌ Error: Bot token missing from .env")
        return
    print("🤖 Starting Alpha Hunter Hub Dedicated Bot Listener...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("add_drop", airdrop_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
