import asyncio
import logging
from config import TOKEN, FILE

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

logging.basicConfig(filename='bot.log',
                    format='%(asctime)s '
                           'LOGGER=%(name)s '
                           'MODULE=%(module)s.py '
                           'FUNC=%(funcName)s'
                           ' %(levelname)s '
                           '%(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S',
                    level='INFO',
                    encoding='utf8')

logger = logging.getLogger('bot')

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()

# reply keyboard
kb = [[KeyboardButton(text="/start"), KeyboardButton(text='Получить данные по температуре')]]
keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=False)


async def get_data_from_file(file) -> list:
    """Getting temperature value from file data"""
    try:
        with open(file, 'r', encoding="utf-8") as f:
            res = f.read().split()
    except Exception as e:
        logging.error('Can not get data from the file')
    return res


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}! Введи команду.", reply_markup=keyboard)


@dp.message(F.text == 'Получить данные по температуре')
async def get_param_handler(message: Message) -> None:
    try:
        value = await get_data_from_file(FILE)
        await message.answer(f"{value[0]} {value[1]}\nТемпература холодильной камеры ЛРБ:\n{html.bold(value[2])} °C")
    except Exception as e:
        print(e)


@dp.message(F.text != 'Получить данные по температуре')
async def others_handler(message: Message) -> None:
    try:
        await message.answer("Неверно введена команда, введите команду еще раз")
    except Exception as e:
        pass


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot exit")
