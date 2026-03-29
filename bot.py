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


def main_menu():

    return InlineKeyboardMarkup([

        [InlineKeyboardButton("📱 Buy Number",callback_data="buy")],

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

        reply_markup=main_menu()

    )


def get_prices():

    try:

        url=f"{BASE}?api_key={API_KEY}&action=getPrices"

        r=requests.get(url,timeout=20).json()

        operators=[]

        sa=r.get(COUNTRY,{}).get(SERVICE,{})

        for op in sa:

            price=float(sa[op]["cost"])

            count=int(sa[op]["count"])

            if count>0:

                operators.append((op,price,count))

        operators.sort(key=lambda x:x[1])

        return operators

    except Exception as e:

        print("PRICE ERROR:",e)

        return []


async def button(update:Update,context:ContextTypes.DEFAULT_TYPE):

    q=update.callback_query

    await q.answer()

    uid=str(q.from_user.id)

    db=load()


    if q.data=="bal":

        bal=db["users"][uid]["balance"]

        await q.message.reply_text(

        f"💰 Balance: {bal}৳",

        reply_markup=main_menu()

        )


    elif q.data=="buy":

        ops=get_prices()

        if not ops:

            await q.message.reply_text("❌ No South Africa stock")

            return

        kb=[]

        for op,price,count in ops[:15]:

            text=f"{price}$ | {count} pcs"

            kb.append([InlineKeyboardButton(text,callback_data=f"buy_{op}_{price}")])

        kb.append([InlineKeyboardButton("⬅ Back",callback_data="back")])

        await q.message.reply_text(

        "🇿🇦 Select South Africa Number Price:",

        reply_markup=InlineKeyboardMarkup(kb)

        )


    elif "buy_" in q.data:

        data=q.data.split("_")

        operator=data[1]

        price=data[2]

        await buy_number(q,operator,price)


    elif q.data=="back":

        await q.message.reply_text(

        "Main Menu",

        reply_markup=main_menu()

        )


async def buy_number(q,operator,price):

    await q.message.reply_text("🔎 Buying number...")


    try:

        url=f"{BASE}?api_key={API_KEY}&action=getNumber&service={SERVICE}&country={COUNTRY}&operator={operator}"

        res=requests.get(url,timeout=20).text


        if "ACCESS_NUMBER" not in res:

            await q.message.reply_text("❌ Stock empty")

            return


        data=res.split(":")

        act=data[1]

        num="+"+data[2]


        await q.message.reply_text(

        f"📱 Number:\n{num}\n💲 Price: {price}$\n\n⏳ Waiting SMS..."

        )


        for i in range(120):

            await asyncio.sleep(3)

            st=requests.get(

            f"{BASE}?api_key={API_KEY}&action=getStatus&id={act}"

            ).text


            if "STATUS_OK" in st:

                code=st.split(":")[1]

                await q.message.reply_text(

                f"✅ Telegram Code:\n{code}"

                )

                return


            if "STATUS_WAIT_CODE" in st:

                continue


            if "STATUS_CANCEL" in st:

                return


        requests.get(

        f"{BASE}?api_key={API_KEY}&action=setStatus&id={act}&status=8"

        )

        await q.message.reply_text("❌ SMS timeout")


    except Exception as e:

        print("BUY ERROR:",e)

        await q.message.reply_text("❌ API Error")


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
