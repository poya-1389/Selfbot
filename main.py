import asyncio

from bot.main import main
from database.create_tables import create_tables


async def start():

    await create_tables()

    await main()


if __name__ == "__main__":
    asyncio.run(start())
