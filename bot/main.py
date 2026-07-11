import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from config import BOT_TOKEN


bot = Bot(BOT_TOKEN)

dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "سلام \n"
        "به نوا سلف خوش آمدید."
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
