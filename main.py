import asyncio
import traceback
from auto_summary_collector import AutoSummaryCollector
from telethon import TelegramClient, events

from loguru import logger
from config import summary_generator_config as config
from telethon_user_api_tools import generate_summary_by_messages, client
from summary_generator import OneShotAsk


summary_collector = AutoSummaryCollector()


@client.on(events.NewMessage(pattern=r'^/summary\s+(\d+)(?:\s+(\d+))?(?:\s+(.+))?$'))
async def summary_handler(event):
    limit_str = event.pattern_match.group(1)
    summary_length_str = event.pattern_match.group(2)
    chat_id = event.chat_id
    # Check if length of summary passed correct
    try:
        summary_length = int(summary_length_str) if summary_length_str else config.default_summary_length
    except ValueError:
        summary_length = config.default_summary_length

    # Check if summary length too long
    if summary_length > config.max_summary_length:
        summary_length = config.max_summary_length
        await client.send_message(
            chat_id,
            message="The summary length exceeds the maximum allowed "
                     f"limit of {config.max_summary_length} characters. "
                     f"It has been adjusted to {config.max_summary_length}.")
    # Check if number of messages passed correct
    try:
        limit = int(limit_str)
    except ValueError:
        limit = 50
    # Check if messages limit too long
    # Check if messages limit too long
    if limit > config.max_messages_to_gather:
        limit = config.max_messages_to_gather
        await client.send_message(
            chat_id,
            message="The number of messages exceeds the maximum allowed "
                     f"limit of {config.max_messages_to_gather}. "
                     f"It has been adjusted to {config.max_messages_to_gather}."
        )

    summary = await generate_summary_by_messages(chat_id, limit, summary_length)
    # Reply to the user message
    await event.reply(message=summary)


@client.on(events.NewMessage(pattern=r'^/stopautosummary$'))
async def stop_auto_summary_handler(event):
    chat_id = event.chat_id
    summary_collector.stop_collect_messages(chat_id)
    await event.reply("Auto-summarization disabled")


@client.on(events.NewMessage(pattern=r'^/setautosummary\s+(\d+)$'))
async def set_auto_summary_handler(event):
    number_of_messages_str = event.pattern_match.group(1)
    try:
        number_of_messages = int(number_of_messages_str)
    except ValueError:
        number_of_messages = 100
    # Check if messages limit too long

    if number_of_messages > config.max_messages_to_gather:
        number_of_messages = config.max_messages_to_gather
        await client.send_message(
            chat_id,
            message=f"The number of messages exceeds the maximum allowed "
                     f"limit of {config.max_messages_to_gather}. "
                     f"It has been adjusted to {config.max_messages_to_gather}."
        )
    chat_id = event.chat_id
    summary_collector.start_collect_messages(chat_id=chat_id, messages_per_collect=number_of_messages)
    await event.reply(f"Auto-summarization enabled with a threshold of {number_of_messages} messages.")


@client.on(events.NewMessage(pattern=rf"^{config.ask_tag_string}\s+(.+)$"))
async def set_ask_tag_handler(event):
    arg_data = str(event.pattern_match.group(1))  
    if not event.reply_to:
        result = OneShotAsk().invoke(query=arg_data, context=[])
        await event.reply(result)
        return
    reply_to_message = await event.get_reply_message()
    additional_context = []
    if reply_to_message:
        additional_context.append("User mention message content:\n{}".format(str(reply_to_message.message)))
    result = OneShotAsk().invoke(query=arg_data, context=additional_context)
    await event.reply(result)


@client.on(events.NewMessage)
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
        await client.send_message(chat_id, message=message)


async def main():
    await client.start()
    print("Bot is working")
    while True:
        try:
            await client.run_until_disconnected()
        except:
            traceback.print_exc()
            await asyncio.sleep(10)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(main())
