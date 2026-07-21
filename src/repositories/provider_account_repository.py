from src.models.provider_account import ProviderName, ProviderAccount
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ProviderAccountUpsertCreds(BaseModel):
    '''
    access_token and refresh_token hold ciphertext not usable tokens
    '''
    user_id: UUID
    provider: ProviderName
    provider_account_id: str
    account_email: str
    access_token: str
    refresh_token: str | None
    expires_at: datetime
    scopes: list[str]

class ProviderAccountError(Exception):
   "Base class for Provider Account exceptions"

class ProviderAccountOwnershipConflict(ProviderAccountError):
    def __init__(
        self,
        provider: ProviderName,
        provider_account_id: str,
        existing_user_id: UUID | None,
        attempted_user_id: UUID
    ) -> None:
        super().__init__(
            f"{provider} account {provider_account_id} is already connected to "
            f"another user"
        )
        self.provider = provider
        self.provider_account_id = provider_account_id
        self.existing_user_id = existing_user_id
        self.attempted_user_id = attempted_user_id

class ProviderAccountNotFound(ProviderAccountError):
    def __init__(self, account_id: UUID) -> None:
        super().__init__(
            f"The provider account {account_id} was not found"
        )
        self.account_id = account_id

class ProviderAccountRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def get_by_provider_and_account_id(
        self, provider: ProviderName, provider_account_id: str
    ) -> ProviderAccount | None:
        query = select(ProviderAccount).where(
            ProviderAccount.provider_account_id == provider_account_id, 
            ProviderAccount.provider == provider)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def list_by_user(self, user_id: UUID) -> list[ProviderAccount]:
        query = select(ProviderAccount).where(
            ProviderAccount.user_id == user_id)
        results = await self.session.execute(query)
        return list(results.scalars().all())

    async def get_by_id(self, account_id: UUID) -> ProviderAccount | None:
        return await self.session.get(ProviderAccount, account_id)

    async def upsert_credentials(self, creds: ProviderAccountUpsertCreds) -> ProviderAccount:
        existing_account = await self.get_by_provider_and_account_id(
            creds.provider, creds.provider_account_id)
        # Two users should not have access to the same account
        if existing_account is not None and existing_account.user_id != creds.user_id:
            raise ProviderAccountOwnershipConflict(
                provider=creds.provider,
                provider_account_id=creds.provider_account_id,
                existing_user_id=existing_account.user_id,
                attempted_user_id=creds.user_id
            )
        if existing_account is None:
            account = ProviderAccount(
                user_id=creds.user_id,
                provider=creds.provider,
                provider_account_id=creds.provider_account_id,
                account_email=creds.account_email,
                access_token=creds.access_token,
                refresh_token=creds.refresh_token,
                expires_at=creds.expires_at,
                scopes=creds.scopes
            )
            try:
                async with self.session.begin_nested():
                    self.session.add(account)
                    await self.session.flush()
            except IntegrityError as e:
                self.session.expunge(account)
                # Check is asyncpg specific
                if getattr(e.orig, "constraint_name", None) == "uq_provider_accounts_provider_provider_account_id":
                    raise ProviderAccountOwnershipConflict(
                        provider=creds.provider,
                        provider_account_id=creds.provider_account_id,
                        existing_user_id=None,
                        attempted_user_id=creds.user_id
                    ) from e
                raise
        else:
            existing_account.account_email = creds.account_email
            existing_account.access_token = creds.access_token
            if creds.refresh_token is not None:
                existing_account.refresh_token = creds.refresh_token
            existing_account.expires_at = creds.expires_at
            existing_account.scopes = creds.scopes
            account = existing_account
            await self.session.flush()
        
        return account

    async def delete(self, account_id: UUID) -> None:
        account = await self.get_by_id(account_id)
        if account is None:
            return

        await self.session.delete(account)
        await self.session.flush()
        
    async def update_access_token(
        self, account_id: UUID, access_token: str, expires_at: datetime
        ) -> None:
        account = await self.get_by_id(account_id)
        if account is None:
            raise ProviderAccountNotFound(account_id=account_id)
        
        account.access_token = access_token
        account.expires_at = expires_at
        await self.session.flush()
