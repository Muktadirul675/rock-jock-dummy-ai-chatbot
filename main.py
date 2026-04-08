import os
from bot import Bot
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_ACCESS_KEY")

bot = Bot(TOKEN)
bot.run()