import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

API_KEY = "kSv4sToA8J1XnSMdrzCyvOYSAt7EVjKU"
BOT_TOKEN = "8682824157:AAHbEe9794qQnpNKSVqirherACuIcqLCzdc"

BASE_URL = "https://smsbower.com/stubs/handler_api.php"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📲 Getting number...")

    try:
        url = f"{BASE_URL}?api_key={API_KEY}&action=getNumber&service=tgff&country=22"
        res = requests.get(url).text

        if "ACCESS_NUMBER" in res:
            data = res.split(":")
            activation_id = data[1]
            number = data[2]

            await update.message.reply_text(f"📞 Number: {number}\n⏳ Waiting for SMS...")

            for i in range(20):
                await asyncio.sleep(5)  # FIXED

                status_url = f"{BASE_URL}?api_key={API_KEY}&action=getStatus&id={activation_id}"
                status = requests.get(status_url).text

                if "STATUS_OK" in status:
                    code = status.split(":")[1]
                    await update.message.reply_text(f"✅ SMS Code: {code}")
                    return

            await update.message.reply_text("❌ SMS not received.")
        else:
            await update.message.reply_text("❌ No number available.")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))

print("Bot running...")
app.run_polling()
