import sys
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# from telegram_util import telegram_utils
from telegram_util import telegram_utils
from crawling import localpc, serverpc
from sLLM import llmInfer
import yaml
import threading


model, tokenizer = llmInfer.define()
day = '2025-11-03'
time = '10'
start = "서울"
end = "부산"

def yamlfix(answer , public_path : str = "./config/public_config.yaml"):
    # 1. YAML 읽기
    with open(public_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    split_answer = answer.split(" ")
    day = split_answer[0]
    time = split_answer[1]
    start = split_answer[2]
    end = split_answer[3]
    trainN = split_answer[4]
    # 2. 값 수정
    config["targetdate"] = day
    config["targettime"] = int(time)
    config["start"] = start
    config["end"] = end
    config["trainNumber"] = trainN
   
    print(config)
    # 4. 수정된 내용 저장
    with open(public_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, allow_unicode=True, default_flow_style=False , sort_keys=False)

    print("YAML 파일 수정 완료")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    if "시작" in user_text:
        await update.message.reply_text(f"예매 시작합니다.")
        threading.Thread(target=localpc.run, daemon=True).start()

    else:
        await update.message.reply_text(f"sLLM 추론 중....")
        answer = llmInfer.infer(model, tokenizer, user_text)

        #yaml 파일 수정 
        yamlfix(answer)

        await update.message.reply_text(f"sLLM 추론 종료!")
        await update.message.reply_text(f"{answer}")


if __name__ == "__main__":
    token = "8305150892:AAGRgaCdiw5l_Dr2tPVztQceleepBswrEc8"
    app = ApplicationBuilder().token(token).build()

    # app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))
    app.run_polling()