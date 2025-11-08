import sys
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# from telegram_util import telegram_utils
from telegram_util import telegram_utils
from crawling import localpc, serverpc



async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    if "시작" in user_text:
        await update.message.reply_text(f"예매 시작합니다.")
        localpc.run()
    

if __name__ == "__main__":
    token = "8305150892:AAGRgaCdiw5l_Dr2tPVztQceleepBswrEc8"
    app = ApplicationBuilder().token(token).build()

    # app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))

    print("텔레그램 봇 시작")
    app.run_polling()