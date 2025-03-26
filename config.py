import dotenv
from pydantic_settings import BaseSettings


dotenv.load_dotenv()


class SummaryGeneratorConfig(BaseSettings):
    telegram_api_id: int
    telegram_api_hash: str
    telegram_session_phone_number: str
    openai_api_key: str
    telethon_session_name: str
    bot_session_name: str
    bot_token: str
    sessions_path: str
    default_summary_length: int
    max_summary_length: int = 1000
    max_messages_to_gather: int = 1000
    load_from_string_session: None | str = None



summary_generator_config = SummaryGeneratorConfig()
