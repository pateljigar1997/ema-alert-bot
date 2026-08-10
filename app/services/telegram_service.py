import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from telegram import Bot

# Load .env from project root
ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def _validate():
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN is missing in .env")

    if not CHAT_ID:
        raise ValueError("TELEGRAM_CHAT_ID is missing in .env")


async def _send(message: str):
    bot = Bot(token=TOKEN)

    await bot.send_message(
        chat_id=int(CHAT_ID),
        text=message
    )


def notify(message: str) -> None:
    _validate()
    asyncio.run(_send(message))