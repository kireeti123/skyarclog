"""
Encryption module for secure log handling.
"""

import os
import json
from typing import Any, Dict, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from base64 import b64encode, b64decode

class LogEncryption:
    """Handles encryption and decryption of log messages."""
    
    def __init__(self, encryption_key: Optional[str] = None, use_fernet: bool = True):
        """
        Initialize the encryption module.
        
        Args:
            encryption_key: Optional encryption key. If not provided, generates a new one.
            use_fernet: Whether to use Fernet encryption (True) or AES-GCM (False).
        """
        self.use_fernet = use_fernet
        if encryption_key:
            self.key = b64decode(encryption_key)
        else:
            self.key = self._generate_key()
            
        if use_fernet:
            self.fernet = Fernet(b64encode(self.key))
    
    def _generate_key(self) -> bytes:
        """Generate a secure encryption key."""
        if self.use_fernet:
            return Fernet.generate_key()
        return os.urandom(32)  # 256-bit key for AES-GCM
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive an encryption key from a password."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password.encode())
    
    def encrypt_log(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt log data.
        
        Args:
            log_data: Dictionary containing log information.
            
        Returns:
            Dictionary with encrypted log data and metadata.
        """
        log_bytes = json.dumps(log_data).encode()
        
        if self.use_fernet:
            encrypted_data = self.fernet.encrypt(log_bytes)
            return {
                "encrypted_data": b64encode(encrypted_data).decode(),
                "encryption_type": "fernet"
            }
        
        # Use AES-GCM for more control over the encryption process
        iv = os.urandom(12)  # 96-bit IV for AES-GCM
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.GCM(iv)
        )
        encryptor = cipher.encryptor()
        
        encrypted_data = encryptor.update(log_bytes) + encryptor.finalize()
        
        return {
            "encrypted_data": b64encode(encrypted_data).decode(),
            "iv": b64encode(iv).decode(),
            "tag": b64encode(encryptor.tag).decode(),
            "encryption_type": "aes-gcm"
        }
    
    def decrypt_log(self, encrypted_log: Dict[str, str]) -> Dict[str, Any]:
        """
        Decrypt log data.
        
        Args:
            encrypted_log: Dictionary containing encrypted log data and metadata.
            
        Returns:
            Original log data dictionary.
        """
        if encrypted_log["encryption_type"] == "fernet":
            encrypted_data = b64decode(encrypted_log["encrypted_data"])
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data)
        
        # Decrypt AES-GCM
        encrypted_data = b64decode(encrypted_log["encrypted_data"])
        iv = b64decode(encrypted_log["iv"])
        tag = b64decode(encrypted_log["tag"])
        
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.GCM(iv, tag)
        )
        decryptor = cipher.decryptor()
        
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        return json.loads(decrypted_data)
    
    def rotate_key(self) -> str:
        """
        Rotate the encryption key.
        
        Returns:
            New base64-encoded encryption key.
        """
        new_key = self._generate_key()
        if self.use_fernet:
            self.fernet = Fernet(b64encode(new_key))
        self.key = new_key
        return b64encode(new_key).decode()
    
    def export_key(self) -> str:
        """
        Export the current encryption key.
        
        Returns:
            Base64-encoded encryption key.
        """
        return b64encode(self.key).decode()
