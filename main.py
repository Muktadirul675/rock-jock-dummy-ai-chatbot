import os
from dotenv import load_dotenv
from bot import app  # import Flask app from bot.py

load_dotenv()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)