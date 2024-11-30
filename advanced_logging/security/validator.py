"""
Log validator module for tamper detection and integrity verification.
"""

import os
import json
import time
import hashlib
from typing import Any, Dict, List, Optional
from datetime import datetime
from collections import OrderedDict

class LogValidator:
    """Handles log validation and tamper detection."""
    
    def __init__(self, chain_size: int = 100):
        """
        Initialize the validator.
        
        Args:
            chain_size: Number of logs to include in each chain block.
        """
        self.chain_size = chain_size
        self.current_block = []
        self.blocks = []
        self.previous_hash = None
    
    def _calculate_hash(self, data: Any) -> str:
        """Calculate SHA-256 hash of data."""
        return hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()
    
    def _create_block(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a new block with Merkle tree of logs."""
        if not logs:
            return None
            
        # Create Merkle tree
        merkle_tree = self._build_merkle_tree(logs)
        
        block = {
            "timestamp": datetime.utcnow().isoformat(),
            "logs": logs,
            "merkle_root": merkle_tree[0],
            "merkle_tree": merkle_tree,
            "previous_hash": self.previous_hash,
            "nonce": 0
        }
        
        # Add proof of work
        while not self._verify_proof_of_work(block):
            block["nonce"] += 1
        
        return block
    
    def _build_merkle_tree(self, logs: List[Dict[str, Any]]) -> List[str]:
        """Build a Merkle tree from logs."""
        # Hash all logs
        hashes = [self._calculate_hash(log) for log in logs]
        
        # Ensure even number of hashes
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])
        
        # Build tree
        tree = []
        level = hashes
        
        while len(level) > 1:
            tree.extend(level)
            next_level = []
            for i in range(0, len(level), 2):
                combined = level[i] + level[i + 1]
                next_level.append(self._calculate_hash(combined))
            level = next_level
        
        tree.extend(level)  # Add root
        return tree
    
    def _verify_proof_of_work(self, block: Dict[str, Any], difficulty: int = 1) -> bool:
        """Verify proof of work for a block."""
        block_hash = self._calculate_hash(block)
        return block_hash.startswith("0" * difficulty)
    
    def add_log(self, log: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Add a log to the current block.
        
        Args:
            log: Log data to add.
            
        Returns:
            New block if chain_size reached, None otherwise.
        """
        # Add timestamp if not present
        if "timestamp" not in log:
            log["timestamp"] = datetime.utcnow().isoformat()
        
        # Add log to current block
        self.current_block.append(log)
        
        # Create new block if chain_size reached
        if len(self.current_block) >= self.chain_size:
            new_block = self._create_block(self.current_block)
            self.blocks.append(new_block)
            self.previous_hash = self._calculate_hash(new_block)
            self.current_block = []
            return new_block
        
        return None
    
    def verify_chain(self) -> bool:
        """
        Verify the entire chain of blocks.
        
        Returns:
            True if chain is valid, False otherwise.
        """
        for i, block in enumerate(self.blocks):
            # Verify proof of work
            if not self._verify_proof_of_work(block):
                return False
            
            # Verify Merkle tree
            merkle_tree = self._build_merkle_tree(block["logs"])
            if merkle_tree != block["merkle_tree"]:
                return False
            
            # Verify chain link
            if i > 0:
                if block["previous_hash"] != self._calculate_hash(self.blocks[i-1]):
                    return False
        
        return True
    
    def verify_log(self, block_index: int, log_index: int) -> bool:
        """
        Verify a specific log entry.
        
        Args:
            block_index: Index of the block containing the log.
            log_index: Index of the log within the block.
            
        Returns:
            True if log is valid, False otherwise.
        """
        try:
            block = self.blocks[block_index]
            log = block["logs"][log_index]
            
            # Verify log hash is in Merkle tree
            log_hash = self._calculate_hash(log)
            merkle_tree = block["merkle_tree"]
            
            # Find log hash in leaf nodes
            leaf_count = len(block["logs"])
            if log_hash not in merkle_tree[:leaf_count]:
                return False
            
            return True
            
        except (IndexError, KeyError):
            return False
    
    def export_chain(self, filepath: str):
        """
        Export the chain to a file.
        
        Args:
            filepath: Path to export the chain to.
        """
        chain_data = {
            "blocks": self.blocks,
            "current_block": self.current_block,
            "previous_hash": self.previous_hash
        }
        
        with open(filepath, 'w') as f:
            json.dump(chain_data, f, indent=2)
    
    def import_chain(self, filepath: str) -> bool:
        """
        Import a chain from a file and verify it.
        
        Args:
            filepath: Path to import the chain from.
            
        Returns:
            True if chain is valid, False otherwise.
        """
        try:
            with open(filepath, 'r') as f:
                chain_data = json.load(f)
            
            self.blocks = chain_data["blocks"]
            self.current_block = chain_data["current_block"]
            self.previous_hash = chain_data["previous_hash"]
            
            return self.verify_chain()
            
        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            return False
