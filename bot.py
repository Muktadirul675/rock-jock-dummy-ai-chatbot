import os
import telebot
import time
from flask import Flask, request
from agent import CustomerCareAgent, PRODUCT_LIST, ABOUT_TEXT, GREETINGS, model

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# -------------------------------
# Bot Class Logic
# -------------------------------
class BotHandler:
    def __init__(self, fresh_user_days=7):
        self.fresh_user_days = fresh_user_days
        self.user_last_seen = {}

        self.agent = CustomerCareAgent(
            model=model,
            product_list=PRODUCT_LIST,
            about_text=ABOUT_TEXT,
            greetings=GREETINGS,
        )

    def is_fresh_user(self, user_id):
        now = time.time()
        if user_id not in self.user_last_seen:
            return True
        last_seen = self.user_last_seen[user_id]
        return (now - last_seen) > self.fresh_user_days * 24 * 60 * 60

    def update_last_seen(self, user_id):
        self.user_last_seen[user_id] = time.time()

handler = BotHandler()

# -------------------------------
# Webhook Endpoint
# -------------------------------
@app.route("/", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)

    if update.message:
        message = update.message
        user_id = message.from_user.id

        bot.send_chat_action(message.chat.id, 'typing')

        fresh = handler.is_fresh_user(user_id)

        response = handler.agent.get_response(
            message.text if message.text else "",
            user_id=user_id,
            fresh_user=fresh
        )

        bot.send_message(message.chat.id, response)
        handler.update_last_seen(user_id)

    return "OK", 200

# -------------------------------
# Health Check (optional)
# -------------------------------
@app.route("/", methods=["GET"])
def home():
    return "Bot is running", 200

# -------------------------------
# Run Flask App
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))