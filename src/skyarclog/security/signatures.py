"""
Digital signature module for log integrity verification.
"""

import json
import hmac
import hashlib
from typing import Any, Dict, Optional
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa, utils
from cryptography.exceptions import InvalidSignature

class LogSignature:
    """Handles digital signatures for log messages."""
    
    def __init__(self, private_key: Optional[str] = None, public_key: Optional[str] = None):
        """
        Initialize the signature module.
        
        Args:
            private_key: Optional PEM-encoded private key for signing.
            public_key: Optional PEM-encoded public key for verification.
        """
        if private_key:
            self.private_key = serialization.load_pem_private_key(
                private_key.encode(),
                password=None
            )
        else:
            self.private_key = self._generate_key_pair()[0]
            
        if public_key:
            self.public_key = serialization.load_pem_public_key(
                public_key.encode()
            )
        else:
            self.public_key = self.private_key.public_key()
    
    def _generate_key_pair(self) -> tuple:
        """Generate a new RSA key pair."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()
        return private_key, public_key
    
    def sign_log(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sign log data with RSA-PSS.
        
        Args:
            log_data: Dictionary containing log information.
            
        Returns:
            Dictionary with log data and signature.
        """
        # Create a deterministic representation of the log data
        log_bytes = json.dumps(log_data, sort_keys=True).encode()
        
        # Calculate log hash
        log_hash = hashlib.sha256(log_bytes).digest()
        
        # Sign the hash
        signature = self.private_key.sign(
            log_hash,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            utils.Prehashed(hashes.SHA256())
        )
        
        # Add HMAC for quick integrity check
        hmac_key = os.urandom(32)
        hmac_obj = hmac.new(hmac_key, log_bytes, hashlib.sha256)
        
        return {
            "log_data": log_data,
            "signature": b64encode(signature).decode(),
            "hmac": b64encode(hmac_obj.digest()).decode(),
            "hmac_key": b64encode(hmac_key).decode()
        }
    
    def verify_log(self, signed_log: Dict[str, Any]) -> bool:
        """
        Verify log signature and integrity.
        
        Args:
            signed_log: Dictionary containing log data and signature.
            
        Returns:
            True if signature is valid, False otherwise.
        """
        try:
            # First check HMAC for quick integrity verification
            hmac_key = b64decode(signed_log["hmac_key"])
            log_bytes = json.dumps(signed_log["log_data"], sort_keys=True).encode()
            hmac_obj = hmac.new(hmac_key, log_bytes, hashlib.sha256)
            expected_hmac = b64decode(signed_log["hmac"])
            
            try:
                hmac.compare_digest(hmac_obj.digest(), expected_hmac)
            except Exception:
                return False
            
            # Verify RSA signature
            log_hash = hashlib.sha256(log_bytes).digest()
            signature = b64decode(signed_log["signature"])
            
            self.public_key.verify(
                signature,
                log_hash,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                utils.Prehashed(hashes.SHA256())
            )
            return True
            
        except (InvalidSignature, KeyError, json.JSONDecodeError):
            return False
    
    def export_keys(self) -> tuple:
        """
        Export the current key pair.
        
        Returns:
            Tuple of (private_key, public_key) in PEM format.
        """
        private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem.decode(), public_pem.decode()
    
    def rotate_keys(self) -> tuple:
        """
        Generate and set new key pair.
        
        Returns:
            Tuple of (private_key, public_key) in PEM format.
        """
        self.private_key, self.public_key = self._generate_key_pair()
        return self.export_keys()
