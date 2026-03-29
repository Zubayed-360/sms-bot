import requests
import asyncio
import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN="8682824157:AAHbEe9794qQnpNKSVqirherACuIcqLCzdc"
API_KEY="KXn60EyIVwdQIwp0CnScWv04SP5mPGgq"

ADMIN_ID=7921810762

BASE="https://smsbower.com/stubs/handler_api.php"

COUNTRY="27"
SERVICE="tg"

FALLBACK=["3205","2742","2812","2840","3109","3160","2217"]


def menu():

    return InlineKeyboardMarkup([

        [InlineKeyboardButton("📱 Buy Number",callback_data="buy")],

        [InlineKeyboardButton("💰 Balance",callback_data="bal")]

    ])


async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(

        "🇿🇦 South Africa Telegram Numbers",

        reply_markup=menu()

    )


def get_prices():

    try:

        r=requests.get(

        f"{BASE}?api_key={API_KEY}&action=getPrices"

        ).json()

        data=[]

        if COUNTRY in r:

            if SERVICE in r[COUNTRY]:

                for op in r[COUNTRY][SERVICE]:

                    price=float(r[COUNTRY][SERVICE][op]["cost"])

                    count=int(r[COUNTRY][SERVICE][op]["count"])

                    if count>0:

                        data.append((op,price,count))

        if not data:

            for op in FALLBACK:

                data.append((op,0.05,100))

        data.sort(key=lambda x:x[1])

        return data

    except:

        data=[]

        for op in FALLBACK:

            data.append((op,0.05,100))

        return data


async def button(update:Update,context:ContextTypes.DEFAULT_TYPE):

    q=update.callback_query

    await q.answer()


    if q.data=="buy":

        ops=get_prices()

        kb=[]

        for op,price,count in ops[:12]:

            txt=f"{price}$ | {count} pcs"

            kb.append([InlineKeyboardButton(txt,callback_data=f"op_{op}_{price}")])

        await q.message.reply_text(

        "Select Price:",

        reply_markup=InlineKeyboardMarkup(kb)

        )


    elif "op_" in q.data:

        data=q.data.split("_")

        operator=data[1]

        price=data[2]

        await buy(q,operator,price)


async def buy(q,operator,price):

    await q.message.reply_text("🔎 Buying number...")


    try:

        res=requests.get(

        f"{BASE}?api_key={API_KEY}&action=getNumber&service={SERVICE}&country={COUNTRY}&operator={operator}"

        ).text


        if "ACCESS_NUMBER" not in res:

            await q.message.reply_text("❌ Try another operator")

            return


        d=res.split(":")

        act=d[1]

        num="+"+d[2]


        await q.message.reply_text(

        f"📱 Number:\n{num}\n💲 {price}$\n\n⏳ Waiting SMS..."

        )


        for i in range(120):

            await asyncio.sleep(3)

            st=requests.get(

            f"{BASE}?api_key={API_KEY}&action=getStatus&id={act}"

            ).text


            if "STATUS_OK" in st:

                code=st.split(":")[1]

                await q.message.reply_text(

                f"✅ Code:\n{code}"

                )

                return


        requests.get(

        f"{BASE}?api_key={API_KEY}&action=setStatus&id={act}&status=8"

        )

        await q.message.reply_text("❌ SMS timeout")


    except:

        await q.message.reply_text("API error")


app=ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start",start))

app.add_handler(CallbackQueryHandler(button))

print("Running")

app.run_polling()
