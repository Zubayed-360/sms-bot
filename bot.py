import requests
import asyncio
import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN="8682824157:AAHbEe9794qQnpNKSVqirherACuIcqLCzdc"
API_KEY="kSv4sToA8J1XnSMdrzCyvOYSAt7EVjKU"

ADMIN_ID=7921810762

BASE="https://smsbower.com/stubs/handler_api.php"

DB="db.json"

COUNTRY="27"
SERVICE="tg"


def load():

    try:
        with open(DB) as f:
            return json.load(f)

    except:
        return {"users":{}}


def save(data):

    with open(DB,"w") as f:
        json.dump(data,f,indent=4)


def menu():

    return InlineKeyboardMarkup([

        [InlineKeyboardButton("📱 Buy South Africa Number",callback_data="buy")],

        [InlineKeyboardButton("💰 Balance",callback_data="bal")]

    ])


async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):

    uid=str(update.effective_user.id)

    db=load()

    if uid not in db["users"]:

        db["users"][uid]={

            "balance":0

        }

        save(db)


    bal=db["users"][uid]["balance"]


    await update.message.reply_text(

        f"👋 Welcome\n\n🇿🇦 South Africa Telegram Numbers\n💰 Balance: {bal}৳",

        reply_markup=menu()

    )


async def button(update:Update,context:ContextTypes.DEFAULT_TYPE):

    q=update.callback_query

    await q.answer()

    uid=str(q.from_user.id)

    db=load()


    if q.data=="bal":

        bal=db["users"][uid]["balance"]

        await q.message.reply_text(

            f"💰 Balance: {bal}৳",

            reply_markup=menu()

        )


    elif q.data=="buy":

        await buy_number(q)



async def buy_number(q):

    await q.message.reply_text("🔎 Finding South Africa number...")


    found=False


    for i in range(10):

        try:

            res=requests.get(

            f"{BASE}?api_key={API_KEY}&action=getNumber&service=tg&country=27",

            timeout=15

            ).text


            if "ACCESS_NUMBER" in res:

                data=res.split(":")

                raw=data[2]


                if raw.startswith("27"):

                    act=data[1]

                    num="+"+raw

                    found=True

                    break


        except:

            pass



    if not found:

        await q.message.reply_text("❌ South Africa stock empty")

        return



    await q.message.reply_text(

    f"📱 Number:\n{num}\n\n⏳ Waiting SMS..."

    )



    for i in range(80):

        await asyncio.sleep(3)


        try:

            st=requests.get(

            f"{BASE}?api_key={API_KEY}&action=getStatus&id={act}",

            timeout=15

            ).text


            if "STATUS_OK" in st:

                code=st.split(":")[1]


                await q.message.reply_text(

                f"✅ Telegram Code:\n{code}"

                )

                return


        except:

            pass



    await q.message.reply_text("❌ SMS timeout")



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


    await update.message.reply_text("✅ Balance added")



app=ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start",start))

app.add_handler(CommandHandler("addbalance",add))

app.add_handler(CallbackQueryHandler(button))


print("Bot Running...")

app.run_polling()
