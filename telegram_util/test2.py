from telegram import Bot
import asyncio
import requests

TOKEN = "8305150892:AAGRgaCdiw5l_Dr2tPVztQceleepBswrEc8"

chat_id = "5841652956"

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
data = {
    "chat_id": chat_id,
    "text": "안녕!"
}

response = requests.post(url, data=data)
print(response.json())

## 되는 것 확인함 