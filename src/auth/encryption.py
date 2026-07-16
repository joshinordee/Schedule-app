from cryptography.fernet import MultiFernet
from typing import Protocol 


class TokenCipher(Protocol):
    def encrypt(self, plain_text: str) -> str: ...
    def decrypt(self, cipher_text: str) -> str: ...

class FernetTokenCipher:
    def __init__(self, cipher: MultiFernet):
        self.cipher = cipher

    def encrypt(self, plain_text: str) -> str:
        text = plain_text.encode()
        return self.cipher.encrypt(text).decode()
    
    def decrypt(self, cipher_text: str) -> str:
        text = cipher_text.encode()
        return self.cipher.decrypt(text).decode()