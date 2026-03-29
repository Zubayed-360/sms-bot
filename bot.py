import requests
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN="8682824157:AAHbEe9794qQnpNKSVqirherACuIcqLCzdc"
API_KEY="KXn60EyIVwdQIwp0CnScWv04SP5mPGgq"

BASE="https://smsbower.com/stubs/handler_api.php"

COUNTRY="27"
SERVICE="tg"


def menu():

    return InlineKeyboardMarkup([

        [InlineKeyboardButton("📱 Buy Number",callback_data="buy")]

    ])


async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(

    "South Africa Telegram Numbers",

    reply_markup=menu()

    )


def operators():

    try:

        r=requests.get(

        f"{BASE}?api_key={API_KEY}&action=getPrices"

        ).json()

        ops=[]

        for op in r[COUNTRY][SERVICE]:

            count=int(r[COUNTRY][SERVICE][op]["count"])

            price=r[COUNTRY][SERVICE][op]["cost"]

            if count>0:

                ops.append((op,price,count))

        return ops

    except:

        return []


async def button(update:Update,context:ContextTypes.DEFAULT_TYPE):

    q=update.callback_query

    await q.answer()


    if q.data=="buy":

        ops=operators()

        kb=[]

        for op,price,count in ops[:10]:

            kb.append([

            InlineKeyboardButton(

            f"{price}$ | {count}",

            callback_data=f"buy_{op}"

            )

            ])

        await q.message.reply_text(

        "Select:",

        reply_markup=InlineKeyboardMarkup(kb)

        )


    elif "buy_" in q.data:

        op=q.data.split("_")[1]

        await buy(q,op)


async def buy(q,operator):

    await q.message.reply_text("🔎 Buying number...")


    for i in range(15):

        try:

            res=requests.get(

            f"{BASE}?api_key={API_KEY}&action=getNumber&service={SERVICE}&country={COUNTRY}&operator={operator}"

            ).text


            if "ACCESS_NUMBER" in res:

                d=res.split(":")

                act=d[1]

                num="+"+d[2]


                await q.message.reply_text(

                f"Number:\n{num}\n\nWaiting SMS..."

                )


                for x in range(100):

                    await asyncio.sleep(3)

                    st=requests.get(

                    f"{BASE}?api_key={API_KEY}&action=getStatus&id={act}"

                    ).text


                    if "STATUS_OK" in st:

                        code=st.split(":")[1]

                        await q.message.reply_text(

                        f"Code:\n{code}"

                        )

                        return


                return

        except:

            pass


    await q.message.reply_text(

    "❌ No number available try again"

    )


app=ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start",start))

app.add_handler(CallbackQueryHandler(button))

print("Running")

app.run_polling()
