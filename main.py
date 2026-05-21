"""
<summary>
Точка входа в приложение.
</summary>
"""

from bot import CityBot
from config import BOT_TOKEN, WEATHER_API_KEY


def main() -> None:
    """
    <summary>Запуск приложения</summary>
    """

    # FIX_ME: вынесены токены в config.py
    # старый код:
    # BOT_TOKEN = "..."
    # WEATHER_API_KEY = "..."
    # новый код:
    bot = CityBot(BOT_TOKEN, WEATHER_API_KEY)

    bot.start()


if __name__ == "__main__":
    main()