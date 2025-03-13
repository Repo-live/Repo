from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class DataEncryption:
    def __init__(self):
        self.salt = os.urandom(16)
    
    def generate_key(self, password: str) -> bytes:
        """Generate encryption key from password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt_file(self, file_path: str, password: str) -> tuple[str, bytes]:
        """Encrypt file and return encrypted file path and salt"""
        key = self.generate_key(password)
        f = Fernet(key)
        
        with open(file_path, 'rb') as file:
            file_data = file.read()
        
        encrypted_data = f.encrypt(file_data)
        encrypted_file_path = file_path + '.encrypted'
        
        with open(encrypted_file_path, 'wb') as file:
            file.write(encrypted_data)
        
        return encrypted_file_path, self.salt
    
    def decrypt_file(self, encrypted_file_path: str, password: str, salt: bytes) -> str:
        """Decrypt file and return decrypted file path"""
        self.salt = salt
        key = self.generate_key(password)
        f = Fernet(key)
        
        with open(encrypted_file_path, 'rb') as file:
            encrypted_data = file.read()
        
        decrypted_data = f.decrypt(encrypted_data)
        decrypted_file_path = encrypted_file_path.replace('.encrypted', '.decrypted')
        
        with open(decrypted_file_path, 'wb') as file:
            file.write(decrypted_data)
        
        return decrypted_file_path 