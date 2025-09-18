from flask import Flask, request
import requests
import os

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "my_secret_token")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == VERIFY_TOKEN:
            return challenge
        return "Invalid verification token", 403

    elif request.method == 'POST':
        data = request.json
        for entry in data['entry']:
            for msg_event in entry['messaging']:
                if 'message' in msg_event:
                    sender = msg_event['sender']['id']
                    text = msg_event['message'].get('text', '')

                    # Gửi reply về Messenger
                    reply(sender, f"Bot nhận: {text}")
        return "ok", 200

def reply(recipient_id, text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
