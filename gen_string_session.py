from telethon import TelegramClient

from summary_generator import SummaryGenerator
from config import summary_generator_config as config
from telethon.sessions import StringSession


if __name__ == "__main__":
    with TelegramClient(StringSession(), config.telegram_api_id, config.telegram_api_hash) as client:
        print(client.session.save())
