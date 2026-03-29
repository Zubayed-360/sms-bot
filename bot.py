import requests
import asyncio
import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN="8682824157:AAHbEe9794qQnpNKSVqirherACuIcqLCzdc"
API_KEY="kSv4sToA8J1XnSMdrzCyvOYSAt7EVjKU"

ADMIN_ID=7921810762

BASE="https://smsbower.com/stubs/handler_api.php"

SELL_PRICE=3

DB="db.json"


def load():
    try:
        return json.load(open(DB))
    except:
        return {"users":{}}


def save(data):
    json.dump(data,open(DB,"w"))


async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):

    uid=str(update.effective_user.id)

    db=load()

    if uid not in db["users"]:

        db["users"][uid]={
            "balance":0
        }

        save(db)

    bal=db["users"][uid]["balance"]

    kb=[

    [InlineKeyboardButton("📱 Buy Telegram Number",callback_data="buy")],

    [InlineKeyboardButton("💰 Balance",callback_data="bal")]

    ]

    await update.message.reply_text(

    f"Balance: {bal}৳",

    reply_markup=InlineKeyboardMarkup(kb)

    )


async def button(update:Update,context:ContextTypes.DEFAULT_TYPE):

    q=update.callback_query

    await q.answer()

    uid=str(q.from_user.id)

    db=load()

    if q.data=="bal":

        bal=db["users"][uid]["balance"]

        await q.message.reply_text(f"💰 Balance: {bal}৳")

    if q.data=="buy":

        if db["users"][uid]["balance"]<SELL_PRICE:

            await q.message.reply_text("❌ Low balance")

            return


        await q.message.reply_text("🇿🇦 Finding South Africa number...")

     country="27"

for i in range(5):

    res=requests.get(
    f"{BASE}?api_key={API_KEY}&action=getNumber&service=tg&country={country}"
    ).text

    if "ACCESS_NUMBER" in res:

        data=res.split(":")

        raw_num=data[2]

        if raw_num.startswith("27"):

            act=data[1]

            num="+"+raw_num

            break

else:

    await q.message.reply_text("❌ No South Africa number")

    return

        db["users"][uid]["balance"]-=SELL_PRICE

        save(db)


        await q.message.reply_text(

        f"📱 Number:\n{num}\n\n⏳ Waiting SMS..."

        )


        for i in range(30):

            await asyncio.sleep(5)

            st=requests.get(

            f"{BASE}?api_key={API_KEY}&action=getStatus&id={act}"

            ).text


            if "STATUS_OK" in st:

                code=st.split(":")[1]

                await q.message.reply_text(

                f"✅ Code:\n{code}"

                )

                return


        await q.message.reply_text("❌ Timeout")



async def add(update:Update,context:ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id!=ADMIN_ID:

        return


    uid=context.args[0]

    amount=int(context.args[1])


    db=load()

    if uid not in db["users"]:

        db["users"][uid]={

        "balance":0

        }


    db["users"][uid]["balance"]+=amount

    save(db)


    await update.message.reply_text("Balance added")


app=ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start",start))

app.add_handler(CommandHandler("addbalance",add))

app.add_handler(CallbackQueryHandler(button))


print("Running")

app.run_polling()
