import asyncio
import logging

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

import config

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Создаем диспетчер
dp = Dispatcher(storage=MemoryStorage())


# Создаем состояния для FSM (машины состояний)
class FeedbackStates(StatesGroup):
    waiting_for_message = State()
    waiting_for_admin_reply = State()


# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(text=
                         f"Привет, {message.from_user.first_name}! 👋\n"
                         "Я бот обратной связи. Отправьте мне ваше сообщение, "
                         "и я передам его администратору."
                         )


# Обработчик команды для ответа пользователю (только для админа)
@dp.message(Command("reply"))
async def cmd_reply(message: Message):
    # Преобразуем ADMIN_ID в число для корректного сравнения
    if message.from_user.id != int(config.ADMIN_ID):
        return

    try:
        # Проверяем формат команды
        command_parts = message.text.split(maxsplit=2)
        if len(command_parts) < 3:
            await message.reply(
                "❌ Ошибка! Используйте формат:\n"
                "/reply <user_id> <текст ответа>"
            )
            return

        _, user_id, reply_text = command_parts
        user_id = int(user_id)

        # Отправляем ответ пользователю
        await config.bot.send_message(
            chat_id=user_id,
            text=f"Ответ от администратора:\n\n{reply_text}"
        )
        await message.reply("✅ Ответ успешно отправлен!")

    except ValueError:
        await message.reply(
            "❌ Ошибка! ID пользователя должен быть числом.\n"
            "Используйте формат: /reply <user_id> <текст ответа>"
        )
    except Exception as e:
        await message.reply(f"❌ Ошибка при отправке: {str(e)}")
        logging.error(f"Ошибка в cmd_reply: {e}")


# Изменим обработчик сообщений пользователя
@dp.message(F.text)
async def handle_user_message(message: Message):
    if message.from_user.id == config.ADMIN_ID:
        # Если это не команда reply, то обрабатываем как ответ на пересланное сообщение
        if not message.text.startswith('/reply'):
            if message.reply_to_message and message.reply_to_message.forward_from:
                # Отправляем ответ пользователю
                user_id = message.reply_to_message.forward_from.id
                await config.bot.send_message(
                    user_id,
                    f"Ответ от администратора:\n\n{message.text}"
                )
                await message.reply("✅ Ответ отправлен пользователю")
    else:
        # Пересылаем сообщение администратору с информацией о пользователе
        user_info = (
            f"Сообщение от пользователя:\n"
            f"ID: {message.from_user.id}\n"
            f"Имя: {message.from_user.first_name}\n"
            f"Username: @{message.from_user.username}\n"
            f"Текст: {message.text}"
        )
        await config.bot.send_message(config.ADMIN_ID, user_info)
        await message.reply(
            "Ваше сообщение отправлено администратору! ✅\n"
            "Вы получите ответ в этом чате."
        )


# Функция запуска бота
async def main():
    # Создаём workflow_data для переменных окружения
    dp.workflow_data.update(dict(
        bot=config.bot,
        TOKEN=config.TOKEN,
        ADMIN_ID=config.ADMIN_ID
    ))

    await dp.start_polling(config.bot)


if __name__ == "__main__":
    asyncio.run(main())
