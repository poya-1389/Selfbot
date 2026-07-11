from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger


class Base(DeclarativeBase):
    pass


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True
    )

    approved: Mapped[bool] = mapped_column(
        default=False
    )

    bio_enabled: Mapped[bool] = mapped_column(
        default=False
    )

    name_enabled: Mapped[bool] = mapped_column(
        default=False
    )

    font: Mapped[str] = mapped_column(
        default="normal"
    )
