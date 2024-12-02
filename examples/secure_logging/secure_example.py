"""
Secure logging example with encryption and digital signatures.
"""

import os
from datetime import datetime
from skyarclog import LogManager
from skyarclog.formatters import JSONFormatter
from skyarclog.listeners import FileListener, ElasticsearchListener
from skyarclog.security import LogEncryption, LogSignature, LogValidator

def setup_secure_logging():
    """Setup secure logging with all security features enabled."""
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Initialize security components
    encryptor = LogEncryption(use_fernet=False)  # Use AES-GCM
    signer = LogSignature()
    validator = LogValidator(chain_size=100)
    
    # Export keys for backup
    encryption_key = encryptor.export_key()
    private_key, public_key = signer.export_keys()
    
    print("Generated Keys (store securely):")
    print(f"Encryption Key: {encryption_key}")
    print(f"Private Key: {private_key}")
    print(f"Public Key: {public_key}")
    
    # Get log manager instance
    log_manager = LogManager.get_instance()
    
    # Add JSON formatter
    log_manager.add_formatter(JSONFormatter())
    
    # Add file listener with rotation
    file_listener = FileListener(
        filepath="logs/secure.log",
        rotate=True,
        max_size="10MB",
        backup_count=5
    )
    log_manager.add_listener(file_listener)
    
    # Add Elasticsearch listener with SSL
    es_listener = ElasticsearchListener(
        hosts=["http://localhost:9200"],
        index_prefix="secure-logs",
        username="elastic",
        password="secret",
        ssl_verify=True,
        ca_certs="/path/to/ca.crt"
    )
    log_manager.add_listener(es_listener)
    
    return log_manager, encryptor, signer, validator

def log_secure_event(logger, encryptor, signer, validator, message: str, context: dict):
    """Log an event with all security measures."""
    # Create log entry
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "message": message,
        "context": context
    }
    
    # Sign the log
    signed_log = signer.sign_log(log_entry)
    
    # Encrypt the signed log
    encrypted_log = encryptor.encrypt_log(signed_log)
    
    # Add to validation chain
    validator.add_log(encrypted_log)
    
    # Log the encrypted and signed data
    logger.info("Secure log entry", encrypted_log)

def verify_log_integrity(signer, validator, block_index: int, log_index: int) -> bool:
    """Verify the integrity of a specific log entry."""
    # First verify the log in the chain
    if not validator.verify_log(block_index, log_index):
        return False
    
    # Get the log from the chain
    block = validator.blocks[block_index]
    encrypted_log = block["logs"][log_index]
    
    # Verify the signature
    return signer.verify_log(encrypted_log)

def main():
    # Setup secure logging
    logger, encryptor, signer, validator = setup_secure_logging()
    
    # Log some secure events
    log_secure_event(
        logger, encryptor, signer, validator,
        "User login",
        {
            "user_id": "user123",
            "ip_address": "192.168.1.1",
            "location": "US",
            "device": "iPhone 13"
        }
    )
    
    log_secure_event(
        logger, encryptor, signer, validator,
        "Financial transaction",
        {
            "transaction_id": "tx_789",
            "amount": 1000.00,
            "currency": "USD",
            "status": "completed"
        }
    )
    
    log_secure_event(
        logger, encryptor, signer, validator,
        "API key rotation",
        {
            "key_id": "key_456",
            "service": "payment_gateway",
            "rotation_reason": "scheduled"
        }
    )
    
    # Export the validation chain
    validator.export_chain("logs/chain.json")
    
    # Verify some logs
    print("\nVerifying logs:")
    for block_index in range(len(validator.blocks)):
        for log_index in range(len(validator.blocks[block_index]["logs"])):
            is_valid = verify_log_integrity(signer, validator, block_index, log_index)
            print(f"Log {block_index}:{log_index} - {'Valid' if is_valid else 'Invalid'}")
    
    # Demonstrate key rotation
    print("\nRotating keys:")
    new_encryption_key = encryptor.rotate_key()
    new_private_key, new_public_key = signer.rotate_keys()
    
    print(f"New Encryption Key: {new_encryption_key}")
    print(f"New Private Key: {new_private_key}")
    print(f"New Public Key: {new_public_key}")

if __name__ == "__main__":
    main()
