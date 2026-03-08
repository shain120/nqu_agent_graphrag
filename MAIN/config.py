from dotenv import load_dotenv
import os

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

PDF_PATH = "358146031.pdf"
TIMEZONE = "Asia/Taipei"
YEAR = 2026