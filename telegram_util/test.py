from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"안녕하세요! 메시지를 보내주세요.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    print("사용자가 보낸 메시지:", user_text)
    await update.message.reply_text(f"받은 메시지: {user_text}")

if __name__ == "__main__":
    token = "8305150892:AAGRgaCdiw5l_Dr2tPVztQceleepBswrEc8"
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))

    print("텔레그램 봇 시작")
    app.run_polling()