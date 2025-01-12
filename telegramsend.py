import requests

def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message: {response.text}")

def get_chat_id(input):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    response = requests.get(url)
    if response.status_code == 200:
        updates = response.json()
        for update in updates["result"]:
            chat_id = update["message"]["chat"]["id"]
            username = update["message"]["chat"]["username"]
            if username == input :
                return chat_id
    else:
        return False

BOT_TOKEN = ""
#CHAT_ID = "1868562308"
#MESSAGE = "Hello, this is a test message from your bot!"

#send_telegram_message(BOT_TOKEN, CHAT_ID, MESSAGE)
