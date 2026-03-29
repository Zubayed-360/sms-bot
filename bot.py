import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

API_KEY = "kSv4sToA8J1XnSMdrzCyvOYSAt7EVjKU"
BOT_TOKEN = "8682824157:AAHbEe9794qQnpNKSVqirherACuIcqLCzdc"

BASE_URL = "https://smsbower.com/stubs/handler_api.php"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Loading country & price list...")

    url = f"{BASE_URL}?api_key={API_KEY}&action=getPrices&service=tgff"
    res = requests.get(url).text

    text = "🌍 Country + Price List:\n\n"
    text += res[:3500]
    text += "\n\n📌 Reply with country ID (example: 22)"

    await update.message.reply_text(text)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.text.strip()

    await update.message.reply_text(f"✅ Country selected: {cid}\n📲 Getting number...")

    url = f"{BASE_URL}?api_key={API_KEY}&action=getNumber&service=tgff&country={cid}"
    res = requests.get(url).text

    if "ACCESS_NUMBER" in res:
        data = res.split(":")
        activation_id = data[1]
        number = data[2]

        await update.message.reply_text(f"📞 Number: {number}\n⏳ Waiting SMS...")

        for _ in range(20):
            await asyncio.sleep(5)

            status = requests.get(
                f"{BASE_URL}?api_key={API_KEY}&action=getStatus&id={activation_id}"
            ).text

            if "STATUS_OK" in status:
                code = status.split(":")[1]
                await update.message.reply_text(f"✅ SMS Code: {code}")
                return

        await update.message.reply_text("❌ SMS not received")
    else:
        await update.message.reply_text("❌ No number available")


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot running...")
app.run_polling()
