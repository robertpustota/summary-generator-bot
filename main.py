import asyncio
from auto_summary_collector import AutoSummaryCollector
from telethon import TelegramClient, events

from config import summary_generator_config as config
from telethon_user_api_tools import generate_summary_by_messages


bot_session_name = f"{config.sessions_path}/{config.bot_session_name}"
bot = TelegramClient(bot_session_name, config.telegram_api_id, config.telegram_api_hash)

summary_collector = AutoSummaryCollector()


@bot.on(events.NewMessage(pattern=r'^/summary\s+(\d+)(?:\s+(\d+))?$'))
async def summary_handler(event):
    limit_str = event.pattern_match.group(1)
    summary_length_str = event.pattern_match.group(2)
    # Check if length of summary passed correct
    try:
        summary_length = int(summary_length_str) if summary_length_str else config.default_summary_length
    except ValueError:
        summary_length = config.default_summary_length
    # Check if number of messages passed correct
    try:
        limit = int(limit_str)
    except ValueError:
        limit = 50

    chat_id = event.chat_id
    summary = await generate_summary_by_messages(chat_id, limit, summary_length)
    # Reply to the user message
    await event.reply(message=summary)


@bot.on(events.NewMessage(pattern=r'^/stopautosummary$'))
async def stop_auto_summary_handler(event):
    chat_id = event.chat_id
    summary_collector.stop_collect_messages(chat_id)
    await event.reply("Auto-summarization disabled")


@bot.on(events.NewMessage(pattern=r'^/setautosummary\s+(\d+)$'))
async def set_auto_summary_handler(event):
    number_of_messages_str = event.pattern_match.group(1)
    try:
        number_of_messages = int(number_of_messages_str)
    except ValueError:
        number_of_messages = 100
    chat_id = event.chat_id
    summary_collector.start_collect_messages(chat_id=chat_id, messages_per_collect=number_of_messages)
    await event.reply(f"Auto-summarization enabled with a threshold of {number_of_messages} messages.")


@bot.on(events.NewMessage)
async def auto_summary_collector(event):
    chat_id = event.chat_id
    # Check if chat exist and if auto collector is enabled
    try:
        chat = summary_collector.get_chat(chat_id)
    except ValueError:
        return    
    if chat.collect_auto_summary is False:
        return
    
    # Collect new message
    text = event.raw_text or "<no text>"
    stripped_text = text.strip()
    if stripped_text.startswith('/') or stripped_text == "<no text>" or not stripped_text:
        return
    sender = await event.message.get_sender()
    sender_name = sender.username if sender.username else str(sender.id)
    summary_collector.add_new_message(chat_id, stripped_text, sender_name)

    # Check if collector is ready to generate summary
    if summary_collector.is_full(chat_id):
        summary = summary_collector.generate_summary(chat_id)
        message = f"Summarization of last {chat.messages_per_collect} messages:\n\n{summary}"
        await bot.send_message(chat_id, message=message)


async def main():
    await bot.start(bot_token=config.bot_token)
    print("Bot is working")
    await bot.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
