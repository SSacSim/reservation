from telegram import Bot
import yaml
import requests

try:
    with open('./config/private_config.yaml', "r", encoding="utf-8") as f:
        userInfo =  yaml.safe_load(f)
except:
    raise "사용자 정보가 없습니다. private_config.yaml 파일을 만들어 주세요."


## message 보내기
def send_message(text:str) :
    TOKEN = userInfo["telegramToken"]
    chat_id = userInfo["telegramChatid"]
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }

    response = requests.post(url, data=data)
## 

