import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")


class AppConfig:
    @staticmethod
    def get(name, default=None):
        return os.getenv(name, default)

    APP_NAME = get("APP_NAME", "QtApp")
    APP_VERSION = get("APP_VERSION", "1.0.0")
    UI_FILE = get("UI_FILE", "main_window.ui")

    @classmethod
    def validate(cls):
        if not all([cls.APP_NAME, cls.APP_VERSION, cls.UI_FILE]):
            raise EnvironmentError("Missing required environment variables")
