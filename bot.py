import pandas as pd
from telegram import Update, Document
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)
import os
from datetime import datetime
import tempfile
import nest_asyncio
import asyncio

nest_asyncio.apply()

# 🔐 Replace with your actual Telegram bot token
BOT_TOKEN = "7979685989:AAFGCHa-OISMWpIx5r3bnx1N8S_Gw4vRlmQ"

# 📩 Format each row into the message format you showed earlier
def format_row(row) -> str:
    message = f"""***** {row['Station Name']} *****
Request ID: {row['Request ID']}
PNR(s): {row['PNR']}
Train details: {row['Train']}
Bogie details: {row['Bogie']}

***** THAALI_DETAILS *****
No of pax: {row['No Of Pax']}

***** TIME_DETAILS *****
Date: {row['Date']}
Day: {row['Day']}
Time: {row['Time Of Arrival']}

***** PASSENGER_DETAILS *****
Name: {row['Name']}
Contact Number: {row['Contact Number']}
Whatsapp Number: {row['Whatsapp Number']}
Comments: {row['Comments']}"""
    return message

# 📁 Handle file upload
async def handle_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc: Document = update.message.document
    if not doc.file_name.endswith((".xlsx", ".xls")):
        await update.message.reply_text("❌ Please upload a valid Excel file.")
        return

    # Download Excel to temporary location
    file = await context.bot.get_file(doc.file_id)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
        await file.download_to_drive(tmp_file.name)
        tmp_path = tmp_file.name

    try:
        # Read and sort data
        df = pd.read_excel(tmp_path)
        df = df.sort_values(by="Time Of Arrival")

        # Send each row as a separate message
        for _, row in df.iterrows():
            msg = format_row(row)
            await update.message.reply_text(msg)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error processing file: {e}")
    finally:
        os.remove(tmp_path)

# 🤖 Set up Telegram bot application
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.Document.ALL, handle_excel))

# 🚀 Async runner for Render
async def main():
    print("🤖 Bot is running.")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.wait_until_closed()
    await app.stop()
    await app.shutdown()

asyncio.run(main())
