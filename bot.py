import telebot
import time
from agent import CustomerCareAgent, PRODUCT_LIST, ABOUT_TEXT, GREETINGS, model

class Bot:
    def __init__(self, token, proxy=None, fresh_user_days=7):
        """
        fresh_user_days: How many days without interaction makes a user 'fresh'
        """
        self.token = token
        self.bot = telebot.TeleBot(token)
        self.fresh_user_days = fresh_user_days
        self.user_last_seen = {}  # {user_id: timestamp}

        # Initialize CustomerCareAgent
        self.agent = CustomerCareAgent(
            model=model,
            product_list=PRODUCT_LIST,
            about_text=ABOUT_TEXT,
            greetings=GREETINGS,
        )

        # Handlers
        self.bot.message_handler(commands=['start'])(self.start)
        self.bot.message_handler(func=lambda message: True)(self.handle_message)

    # -------------------------------
    # User freshness tracking
    # -------------------------------
    def is_fresh_user(self, user_id):
        now = time.time()
        if user_id not in self.user_last_seen:
            return True  # Completely new user
        last_seen = self.user_last_seen[user_id]
        if (now - last_seen) > self.fresh_user_days * 24 * 60 * 60:
            return True  # User inactive for fresh_user_days
        return False

    def update_last_seen(self, user_id):
        self.user_last_seen[user_id] = time.time()

    # -------------------------------
    # Handlers
    # -------------------------------
    def start(self, message):
        user_id = message.from_user.id
        fresh = self.is_fresh_user(user_id)
        response = self.agent.get_response("", user_id, fresh_user=fresh)  # Greeting for fresh user
        self.bot.reply_to(message, response)
        self.update_last_seen(user_id)

    def handle_message(self, message):
        user_id = message.from_user.id
        self.bot.send_chat_action(message.chat.id, 'typing')
        fresh = False
        # Get agent response
        response = self.agent.get_response(message.text, user_id=user_id, fresh_user=fresh)
        self.bot.reply_to(message, response)
        self.update_last_seen(user_id)

    # -------------------------------
    # Run bot
    # -------------------------------
    def run(self, timeout=20, long_polling_timeout=20):
        print("Bot is running...")
        self.bot.infinity_polling(timeout=timeout, long_polling_timeout=long_polling_timeout)

