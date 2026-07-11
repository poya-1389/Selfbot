from database.database import SessionLocal
from database.models import User


async def create_user(telegram_id: int):

    async with SessionLocal() as session:

        user = User(
            telegram_id=telegram_id
        )

        session.add(user)

        await session.commit()
