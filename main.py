import asyncio
from telethon import TelegramClient, events

from config import summary_generator_config as config
from telethon_user_api_tools import generate_summary_by_messages


bot_session_name = f"{config.sessions_path}/{config.bot_session_name}"
bot = TelegramClient(bot_session_name, config.telegram_api_id, config.telegram_api_hash)


@bot.on(events.NewMessage(pattern=r'^/summary\s+(\d+)(?:\s+(\d+))?$'))
async def summary_handler(event):
    limit_str = event.pattern_match.group(1)
    summary_length_str = event.pattern_match.group(2)
    # Check if length of summary passed correct
    try:
        summary_length = int(summary_length_str) if summary_length_str else 250
    except ValueError:
        summary_length = 250
    # Check if number of messages passed correct
    try:
        limit = int(limit_str)
    except ValueError:
        limit = 50

    chat_id = event.chat_id
    summary = await generate_summary_by_messages(chat_id, limit, summary_length)
    # Reply to the user message
    await event.reply(message=summary)


async def main():
    await bot.start(bot_token=config.bot_token)
    print("Bot is working")
    await bot.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
