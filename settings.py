from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    AMQP_URL: str = 'amqp://guest:guest@localhost/'
    EXCEL_PATH: str = r'Тестовое.XLSX'


@lru_cache()
def get_settings():
    return Settings()
