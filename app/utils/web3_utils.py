from web3 import Web3
import json
import os
from datetime import datetime
from flask import current_app
from app.extensions import db

# Connect to blockchain provider
def get_web3():
    """Connect to Web3 provider using environment config"""
    provider_url = os.environ.get('WEB3_PROVIDER_URL') or 'http://localhost:8545'
    
    # For HTTP connections
    if provider_url.startswith('http'):
        return Web3(Web3.HTTPProvider(provider_url))
    
    # For WebSocket connections
    elif provider_url.startswith('ws'):
        return Web3(Web3.WebsocketProvider(provider_url))
    
    # For IPC connections
    else:
        return Web3(Web3.IPCProvider(provider_url))

def get_contract(contract_name, address=None):
    """Get contract ABI and address"""
    try:
        # Load contract ABI
        contract_path = os.path.join(current_app.root_path, 'contracts', f'{contract_name}.json')
        with open(contract_path) as f:
            contract_json = json.load(f)
        
        # Connect to Web3
        w3 = get_web3()
        if not w3.isConnected():
            current_app.logger.error("Not connected to Web3 provider")
            return None
            
        # Use provided address or get from contract json
        contract_address = address or contract_json.get('networks', {}).get(str(w3.eth.chainId), {}).get('address')
        if not contract_address:
            current_app.logger.error(f"Contract address not found for {contract_name}")
            return None
            
        # Create contract instance
        contract = w3.eth.contract(
            address=contract_address,
            abi=contract_json['abi']
        )
        
        return contract
    except Exception as e:
        current_app.logger.error(f"Error loading contract {contract_name}: {str(e)}")
        return None

def store_hash_on_blockchain(document_type, document_id, document_hash, metadata=None):
    """Store document hash on blockchain for verification"""
    try:
        # Get contract
        document_registry = get_contract('DocumentRegistry')
        if not document_registry:
            return False, "Unable to connect to Document Registry contract"
        
        # Get Web3 instance
        w3 = get_web3()
        if not w3.isConnected():
            return False, "Not connected to Web3 provider"
            
        # Get account address from environment or use first account
        account = os.environ.get('WEB3_ACCOUNT_ADDRESS') or w3.eth.accounts[0]
        
        # Prepare transaction
        tx_hash = document_registry.functions.registerDocument(
            document_type,
            str(document_id),
            document_hash,
            metadata or ""
        ).transact({'from': account})
        
        # Wait for transaction receipt
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        
        # Check if transaction was successful
        if tx_receipt['status'] == 1:
            # Get the event data
            document_registered = document_registry.events.DocumentRegistered().processReceipt(tx_receipt)
            
            return True, {
                'tx_hash': tx_hash.hex(),
                'block_number': tx_receipt['blockNumber'],
                'timestamp': datetime.now().isoformat(),
                'event_data': document_registered[0]['args'] if document_registered else None
            }
        else:
            return False, "Transaction failed"
            
    except Exception as e:
        current_app.logger.error(f"Error storing hash on blockchain: {str(e)}")
        return False, str(e)

def verify_document_hash(document_type, document_id, document_hash):
    """Verify if document hash matches what's stored on blockchain"""
    try:
        # Get contract
        document_registry = get_contract('DocumentRegistry')
        if not document_registry:
            return False, "Unable to connect to Document Registry contract"
        
        # Call the verification function
        is_valid, registered_by, timestamp = document_registry.functions.verifyDocument(
            document_type,
            str(document_id),
            document_hash
        ).call()
        
        if is_valid:
            return True, {
                'is_valid': is_valid,
                'registered_by': registered_by,
                'timestamp': datetime.fromtimestamp(timestamp).isoformat()
            }
        else:
            return False, "Document hash does not match blockchain record"
            
    except Exception as e:
        current_app.logger.error(f"Error verifying hash on blockchain: {str(e)}")
        return False, str(e)