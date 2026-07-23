from src.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid, String, DateTime, func
import uuid
from datetime import datetime
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.models.provider_account import ProviderAccount


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(300), unique=True)
    display_name: Mapped[str] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    provider_accounts: Mapped[list["ProviderAccount"]] = relationship(
        "ProviderAccount",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
