from src.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import (
    UniqueConstraint, 
    Uuid, 
    String, 
    DateTime, 
    func, 
    LargeBinary, 
    ARRAY, 
    ForeignKey, 
    Enum as SQLEnum
)
from enum import Enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.models.user import User


class ProviderName(str, Enum):
    GOOGLE = "google"


class ProviderAccount(Base):
    __tablename__ = "provider_accounts"
    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_account_id",
            name="uq_provider_accounts_provider_provider_account_id"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    provider: Mapped[ProviderName] = mapped_column(
        SQLEnum(
            ProviderName, 
            name="provider_name",
            values_callable=lambda enum: [member.value for member in enum]
        )
    )
    provider_account_id: Mapped[str] = mapped_column(String(300))
    account_email: Mapped[str] = mapped_column(String(300))
    access_token: Mapped[bytes] = mapped_column(LargeBinary)
    refresh_token: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    scopes: Mapped[list[str]] = mapped_column(MutableList.as_mutable(ARRAY(String(500))))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="provider_accounts"
    )
