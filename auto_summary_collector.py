from pydantic import BaseModel

from telethon_user_api_tools import summary_generator
from config import summary_generator_config as config


class Chat(BaseModel):
    collect_auto_summary: bool = False
    auto_summary_messages: list
    messages_per_collect: int = 100


class AutoSummaryCollector:
    def __init__(self):
        self.chats = dict()

    def get_chat(self, chat_id):
        chat = self.chats.get(chat_id)
        if not chat:
            raise ValueError("There is no chat with this ID")
        return chat

    def start_collect_messages(self, chat_id: str, messages_per_collect: int):
        chat = self.chats.get(chat_id)
        if not chat:
            self.chats[chat_id] = Chat(
                collect_auto_summary=True,
                auto_summary_messages=[],
                messages_per_collect=messages_per_collect)
        else:
            chat.collect_auto_summary = True
            chat.auto_summary_messages = []
            chat.messages_per_collect = messages_per_collect

    def stop_collect_messages(self, chat_id: str):
        chat = self.get_chat(chat_id)
        chat.auto_summary_messages.clear()
        chat.collect_auto_summary = False

    def add_new_message(self, chat_id, message, sender):
        chat = self.get_chat(chat_id)
        combined_message = f"{sender}: {message}"
        chat.auto_summary_messages.append(combined_message)

    def generate_summary(self, chat_id: str) -> list[str]:
        chat = self.get_chat(chat_id)
        messages_list = chat.auto_summary_messages.copy()
        chat.auto_summary_messages.clear()
        summary = summary_generator.invoke(messages_list, config.default_summary_length)
        return summary

    def is_full(self, chat_id: str) -> bool:
        chat = self.get_chat(chat_id)
        return len(chat.auto_summary_messages) >= chat.messages_per_collect
