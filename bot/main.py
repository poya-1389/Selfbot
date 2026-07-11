import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from database.crud import create_user

from config import BOT_TOKEN


bot = Bot(BOT_TOKEN)

dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: Message):

    await create_user(
        message.from_user.id
    )

    await message.answer(
        "سلام \n"
        "به ربات نوا سلف خوش آمدید ثبت نام اولیه انجام شد."
    )

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
