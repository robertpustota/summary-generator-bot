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

summary_generator_config = SummaryGeneratorConfig()
