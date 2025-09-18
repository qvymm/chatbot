from flask import Flask, request
import requests
import os
import google.generativeai as genai

app = Flask(__name__)

# --- Config ---
VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN", "my_secret_token")
PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini init
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# --- Routes ---
@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Facebook verification
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == VERIFY_TOKEN:
            return challenge
        return "Invalid verification token", 403

    elif request.method == 'POST':
        data = request.json
        if data.get("object") == "page":
            for entry in data['entry']:
                for event in entry['messaging']:
                    if 'message' in event and 'text' in event['message']:
                        sender_id = event['sender']['id']
                        user_text = event['message']['text']

                        # Gọi Gemini để sinh trả lời
                        try:
                            response = model.generate_content(user_text)
                            reply_text = response.text
                        except Exception as e:
                            reply_text = f"Lỗi gọi Gemini: {e}"

                        send_message(sender_id, reply_text)

        return "ok", 200

def send_message(recipient_id, text):
    """Send message back to Messenger"""
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    r = requests.post(url, json=payload)
    if r.status_code != 200:
        print("Error sending:", r.text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
