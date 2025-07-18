from sqlalchemy import (
    BigInteger,
    ForeignKey,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class MessageDB(Base):
    __tablename__ = "messages"

    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), nullable=False)
    chat_db: Mapped["ChatDB"] = relationship(
        back_populates="messages",
        lazy="selectin",
    )
    role: Mapped[str] = mapped_column(String(15), nullable=False)
    content: Mapped[str] = mapped_column(String(2000), nullable=False)
    timestamp: Mapped[int] = mapped_column(BigInteger, nullable=False)


class ChatDB(Base):
    __tablename__ = "chats"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    user_db: Mapped["UserDB"] = relationship(
        back_populates="chats",
    )
    chat_name: Mapped[str] = mapped_column(String(100), nullable=True)
    messages: Mapped[list["MessageDB"]] = relationship(
        back_populates="chat_db",
        lazy="selectin",
        cascade="all, delete-orphan",
    )


class UserDB(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String(50), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=True)

    chats: Mapped[list["ChatDB"]] = relationship(
        back_populates="user_db",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
