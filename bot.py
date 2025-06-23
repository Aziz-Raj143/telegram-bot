import asyncio
import nest_asyncio
import logging
from flask import Flask
from telegram.ext import ApplicationBuilder, MessageHandler, filters
import pandas as pd
from io import BytesIO

# Your bot token (replace this or use environment variable)
import os
BOT_TOKEN = os.getenv("BOT_TOKEN", "7979685989:AAFGCHa-OISMWpIx5r3bnx1N8S_Gw4vRlmQ")

# Logging
logging.basicConfig(level=logging.INFO)

# Flask app to keep web service running
web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Bot is running!", 200

# Telegram bot logic
async def handle_file(update, context):
    file = await update.message.document.get_file()
    f = BytesIO()
    await file.download_to_memory(out=f)
    f.seek(0)
    df = pd.read_excel(f)

    # Sort by "Time Of Arrival"
    df = df.sort_values(by="Time Of Arrival")

    for _, row in df.iterrows():
        msg = f"🚆 Train No: {row['Train No']}\n📍 Station: {row['Station Name']}\n🕐 ETA: {row['Time Of Arrival']}"
        await update.message.reply_text(msg)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

# Run Telegram bot inside async loop
async def run_bot():
    print("🤖 Bot is running.")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.wait_until_closed()

# Apply nest_asyncio for compatibility
nest_asyncio.apply()

# Start both Flask and Telegram bot
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    web_app.run(host="0.0.0.0", port=10000)
