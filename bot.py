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

PRICES={
"3237":3,
"3205":3,
"2840":3,
"3109":3
}


def load():

    try:
        return json.load(open(DB))

    except:
        return {"users":{}}


def save(data):

    json.dump(data,open(DB,"w"))


def menu(bal):

    kb=[

    [InlineKeyboardButton("📱 Buy Number",callback_data="buy")],

    [InlineKeyboardButton("📊 Price List",callback_data="price")],

    [InlineKeyboardButton("💰 Balance",callback_data="bal")]

    ]

    return InlineKeyboardMarkup(kb)


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

    f"👋 Welcome\n\n💰 Balance: {bal}৳",

    reply_markup=menu(bal)

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

        reply_markup=menu(bal)

        )


    if q.data=="buy":

        kb=[

        [InlineKeyboardButton("💎 Gold 3৳",callback_data="3237")],

        [InlineKeyboardButton("🥉 Bronze 3৳",callback_data="3205")],

        [InlineKeyboardButton("🥈 Silver 3৳",callback_data="2840")],

        [InlineKeyboardButton("🔙 Back",callback_data="menu")]

        ]


        await q.message.reply_text(

        "Select Number Price:",

        reply_markup=InlineKeyboardMarkup(kb)

        )


    if q.data=="price":

        await q.message.reply_text(

        "📊 Telegram Price List\n\nGold = 3৳\nBronze = 3৳\nSilver = 3৳",

        reply_markup=menu(db["users"][uid]["balance"])

        )


    if q.data=="menu":

        bal=db["users"][uid]["balance"]

        await q.message.reply_text(

        "Main Menu",

        reply_markup=menu(bal)

        )


    if q.data in PRICES:

        price=PRICES[q.data]

        if db["users"][uid]["balance"]<price:

            await q.message.reply_text("❌ Low balance")

            return


        await q.message.reply_text("🔎 Buying number...")


        res=requests.get(

        f"{BASE}?api_key={API_KEY}&action=getNumber&service=tg&country={COUNTRY}&operator={q.data}"

        ).text


        if "ACCESS_NUMBER" not in res:

            await q.message.reply_text("❌ Stock empty")

            return


        data=res.split(":")

        act=data[1]

        num="+"+data[2]


        db["users"][uid]["balance"]-=price

        save(db)


        await q.message.reply_text(

        f"📱 Number:\n{num}\n\n⏳ Waiting SMS..."

        )


        for i in range(60):

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


print("Running...")

app.run_polling()
