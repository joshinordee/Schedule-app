from functools import lru_cache
from cryptography.fernet import Fernet, MultiFernet
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Secret, SecretStr


class Settings(BaseSettings):
    database_url: SecretStr
    #token_cipher_key: SecretStr
    google_client_id: SecretStr
    google_client_secret: SecretStr
    google_redirect_uri: str
    google_scopes: str


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def scopes(self) -> list[str]:
        return [scope.strip() for scope in self.google_scopes.split(",")]
'''
    def token_cipher(self) -> MultiFernet:
        raw_keys_str = self.token_cipher_key.get_secret_value()
        key_list = [k.strip() for k in raw_keys_str.split(",")]
        fernet_instances = [Fernet(key.encode()) for key in key_list if key]
            
        if not fernet_instances:
            raise ValueError("token_cipher_key must contain at least one valid Fernet key.")
                
        return MultiFernet(fernet_instances)
'''

@lru_cache
def get_settings() -> Settings:
    return Settings()
