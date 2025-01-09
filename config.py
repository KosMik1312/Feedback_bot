import os
from aiogram import Bot

from dotenv import load_dotenv


# Загружаем TOKEN и API_KEY
load_dotenv()

TOKEN = os.getenv("TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Настройки бота / для работы с PythonAnyWhere нужно добавить session=session
bot = Bot(token=TOKEN)  # Объект бота

