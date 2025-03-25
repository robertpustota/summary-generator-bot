from telethon import TelegramClient

from summary_generator import SummaryGenerator
from config import summary_generator_config as config

summary_generator = SummaryGenerator(
    llm_model='openai/gpt-4o-mini',
    llm_model_kwargs={"api_key": config.openai_api_key})

session_name = f"{config.sessions_path}/{config.telethon_session_name}"
client = TelegramClient(session_name, config.telegram_api_id, config.telegram_api_hash)


async def generate_summary_by_messages(chat_id: str, messages_limit: int, summary_length: int):
    """
    Generates a summary of messages from a specified chat.
    This asynchronous function retrieves a specified number of messages from a chat,
    filters and processes them, and then generates a summary based on the collected
    chat history.
    Args:
        chat_id (int or str): The ID or username of the chat to retrieve messages from.
        messages_limit (int): The maximum number of messages to retrieve from the chat.
        summary_length (int): The desired length of the generated summary.
    Returns:
        str: A summary of the chat messages.
    Notes:
        - Messages starting with '/summary', empty messages, or messages with no text
          are excluded from the summary.
        - The function assumes the existence of a `client` object for interacting with
          the Telegram API and a `summary_generator` object for generating summaries.
        - The function must be called within an asynchronous context.
    """
    await client.start()

    messages = await client.get_messages(chat_id, limit=messages_limit)
    # Collecting messages
    collected_messages = []
    for msg in reversed(messages):
        sender = await msg.get_sender()
        sender_name = sender.username if sender.username else str(sender.id)
        text = msg.message or "<no text>"
        stripped_text = text.strip()
        if stripped_text.startswith('/summary') or stripped_text == "<no text>" or not stripped_text:
            continue
        collected_messages.append(f"{sender_name}: {stripped_text}")

    summary = summary_generator.invoke(chat_history=collected_messages, 
                                        summary_length=summary_length)
    return summary
