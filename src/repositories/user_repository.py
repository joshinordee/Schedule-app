from src.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from pydantic import BaseModel
from uuid import UUID


class UserCreate(BaseModel):
    email: str
    display_name: str

class UserError(Exception):
    "Base class for User exceptions"

class UserExistsConflict(UserError):
    def __init__(self, email: str) -> None:
        super().__init__(
            f"Email: {email} is already in use"
        )
        self.email = email
        
class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_id(self, user_id: UUID) -> User | None:
        return await self.session.get(User, user_id)
    
    async def create(self, user_data: UserCreate) -> User:
        user = User(
            email=user_data.email, 
            display_name=user_data.display_name
        )
        try:
            # .begin_nested instead of a rollback so that the entire transaction isn't 
            # discarded
            async with self.session.begin_nested():
                self.session.add(user)
                await self.session.flush()
        except IntegrityError as e: 
            if getattr(e.orig, "constraint_name", None) == "uq_users_email": # Check is asyncpg specific
                raise UserExistsConflict(email=user_data.email) from e
            raise
        return user
