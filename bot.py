import telebot as tb
from telebot import types
import random
import requests
from typing import Dict, Any, List

from config import WEATHER_BASE_URL


class CityBot:
    """
    <summary>
    Telegram-бот для получения информации о городах.
    </summary>
    """

    def __init__(self, token: str, weather_api_key: str) -> None:
        self.bot = tb.TeleBot(token)
        self.weather_api_key = weather_api_key

        # FIX_ME: список оформлен по PEP 8 (читабельность)
        self.cities: List[str] = [
            "Москва",
            "Санкт-Петербург",
            "Пермь",
            "Казань",
            "Екатеринбург"
        ]

        self.user_states: Dict[int, Dict[str, Any]] = {}

        self._setup_commands()
        self._setup_handlers()

    def _setup_commands(self) -> None:
        self.bot.set_my_commands([
            tb.types.BotCommand("/start", "Начать"),
            tb.types.BotCommand("/bye", "Выход"),
            tb.types.BotCommand("/help", "Список городов")
        ])

    def _setup_handlers(self) -> None:

        @self.bot.message_handler(commands=['start'])
        def start_handler(message: types.Message) -> None:
            self._send_welcome(message)

        @self.bot.message_handler(commands=['bye'])
        def bye_handler(message: types.Message) -> None:
            self._send_bye(message)

        @self.bot.message_handler(commands=['help'])
        def help_handler(message: types.Message) -> None:
            self._send_list_cities(message)

        @self.bot.message_handler(content_types=['photo'])
        def photo_handler(message: types.Message) -> None:
            self._photo_processing(message)

        # FIX_ME: упрощена передача функции без lambda
        # старый код:
        # func=lambda message: self._is_city_message(message)
        # новый код:
        @self.bot.message_handler(func=self._is_city_message)
        def city_handler(message: types.Message) -> None:
            self._process_city(message)

        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_handler(call: types.CallbackQuery) -> None:
            self._handle_callback(call)

        @self.bot.message_handler()
        def default_handler(message: types.Message) -> None:
            self._unknown_command(message)

    def _is_city_message(self, message: types.Message) -> bool:

        # FIX_ME: убрано дублирование списка городов
        # старый код:
        # cities_lower = [city.lower() for city in self.cities]
        # return user_text in cities_lower

        return (
            message.text is not None and
            message.text.strip().lower() in
            [city.lower() for city in self.cities]
        )

    def _process_city(self, message: types.Message) -> None:

        # FIX_ME: убран index и лишний поиск
        # старый код:
        # city_index = cities_lower.index(user_city)
        # original_city = self.cities[city_index]

        city = message.text.strip()

        self.user_states[message.chat.id] = {"city": city}
        self._show_city_menu(message.chat.id, city)

    def _send_welcome(self, message: types.Message) -> None:

        # FIX_ME: упрощён текст (читабельность)
        text = (
            f"Здравствуйте, {message.from_user.first_name}!\n\n"
            "Введите город и выберите действие"
        )

        self.bot.send_message(message.chat.id, text)

    def _send_bye(self, message: types.Message) -> None:
        self.bot.send_message(
            message.chat.id,
            f"До свидания, {message.from_user.first_name}!"
        )

    def _send_list_cities(self, message: types.Message) -> None:
        cities_text = "\n".join(f"• {city}" for city in self.cities)
        self.bot.send_message(message.chat.id, cities_text)

    def _unknown_command(self, message: types.Message) -> None:
        self.bot.reply_to(message, "Введите город или /help")

    def _show_city_menu(self, chat_id: int, city: str) -> None:
        markup = types.InlineKeyboardMarkup()

        # FIX_ME: упрощено создание кнопок
        # старый код:
        # markup.row(...)
        # новый код:
        markup.add(types.InlineKeyboardButton(
            "📖 Справка", callback_data=f"info_{city}"
        ))
        markup.add(
            types.InlineKeyboardButton(
                "📸 Фото", callback_data=f"photo_{city}"
            ),
            types.InlineKeyboardButton(
                "🌤 Погода", callback_data=f"weather_{city}"
            )
        )

        self.bot.send_message(chat_id, f"Город: {city}", reply_markup=markup)

    def _handle_callback(self, call: types.CallbackQuery) -> None:

        # FIX_ME: убрано дублирование split
        # старый код:
        # city = call.data.split('_')[1]

        action, city = call.data.split("_")

        if action == "info":
            self._show_city_info(call.message.chat.id, city)
        elif action == "photo":
            self._show_city_photo(call.message.chat.id, city)
        elif action == "weather":
            self._show_city_weather(call.message.chat.id, city)

    def _show_city_info(self, chat_id: int, city: str) -> None:
        data = {
            "Москва": "Россия, 13 млн",
            "Санкт-Петербург": "Россия, 5.6 млн",
            "Пермь": "Россия, 1 млн",
            "Казань": "Россия, 1.5 млн",
            "Екатеринбург": "Россия, 1.5 млн"
        }

        self.bot.send_message(chat_id, data.get(city, "Нет данных"))

    def _show_city_photo(self, chat_id: int, city: str) -> None:
        photos = {
            "Москва": "https://upload.wikimedia.org/wikipedia/commons/a/a3/Moscow_Montage_2016.png",
            "Санкт-Петербург": "https://upload.wikimedia.org/wikipedia/commons/c/cd/SPB_Montage_2016.png"
        }

        url = photos.get(city)

        if url:
            self.bot.send_photo(chat_id, url)
        else:
            self.bot.send_message(chat_id, "Фото не найдено")

    def _show_city_weather(self, chat_id: int, city: str) -> None:
        params = {
            "access_key": self.weather_api_key,
            "query": city,
            "units": "m"
        }

        try:
            response = requests.get(
                WEATHER_BASE_URL,
                params=params,
                timeout=5
            )

            data = response.json()

            # FIX_ME: упрощена проверка температуры
            # старый код:
            # if temp_celsius != "Н/Д":

            temp = data.get("current", {}).get("temperature")

            if temp is None:
                raise ValueError

            self.bot.send_message(
                chat_id,
                f"Температура в {city}: {temp}°C"
            )

        except Exception:
            self.bot.send_message(chat_id, "Ошибка погоды")

    def _photo_processing(self, message: types.Message) -> None:

        # FIX_ME: убран random.sample
        # старый код:
        # random.sample(list_of_phrases, 3)

        phrases = [
            "Классное фото!",
            "Очень атмосферно!",
            "Круто!",
            "Отличный кадр!"
        ]

        self.bot.reply_to(message, random.choice(phrases))

    def start(self) -> None:
        print("Бот запущен...")
        self.bot.infinity_polling()