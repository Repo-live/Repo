from web3 import Web3
import json
import os

class BlockchainManager:
    def __init__(self, contract_address, node_url):
        self.web3 = Web3(Web3.HTTPProvider(node_url))
        self.contract_address = contract_address
        
        with open('contracts/DataMarket.json', 'r') as f:
            contract_json = json.load(f)
        
        self.contract = self.web3.eth.contract(
            address=contract_address,
            abi=contract_json['abi']
        )
    
    def list_dataset(self, metadata_hash, price, description, size, data_type, account):
        nonce = self.web3.eth.get_transaction_count(account.address)
        
        transaction = self.contract.functions.listDataset(
            metadata_hash,
            price,
            description,
            size,
            data_type
        ).build_transaction({
            'from': account.address,
            'gas': 2000000,
            'nonce': nonce,
        })
        
        signed_txn = self.web3.eth.account.sign_transaction(
            transaction, account.private_key
        )
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)
    
    def add_dataset_version(self, dataset_id: int, metadata_hash: str, 
                          description: str, changelog: str, account) -> dict:
        """Add new version to existing dataset"""
        nonce = self.web3.eth.get_transaction_count(account.address)
        
        transaction = self.contract.functions.addDatasetVersion(
            dataset_id,
            metadata_hash,
            description,
            changelog
        ).build_transaction({
            'from': account.address,
            'gas': 2000000,
            'nonce': nonce,
        })
        
        signed_txn = self.web3.eth.account.sign_transaction(
            transaction, account.private_key
        )
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)
    
    def get_dataset_versions(self, dataset_id: int) -> list:
        """Get all versions of a dataset"""
        versions = self.contract.functions.getDatasetVersions(dataset_id).call()
        return [
            {
                'metadata_hash': v[0],
                'description': v[1],
                'timestamp': v[2],
                'changelog': v[3]
            }
            for v in versions
        ]
    
    def update_dataset_category(self, dataset_id: int, category_id: int, account) -> dict:
        """Update dataset category"""
        nonce = self.web3.eth.get_transaction_count(account.address)
        
        transaction = self.contract.functions.updateDatasetCategory(
            dataset_id,
            category_id
        ).build_transaction({
            'from': account.address,
            'gas': 2000000,
            'nonce': nonce,
        })
        
        signed_txn = self.web3.eth.account.sign_transaction(
            transaction, account.private_key
        )
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)
    
    def update_dataset_tags(self, dataset_id: int, tags: list, account) -> dict:
        """Update dataset tags"""
        nonce = self.web3.eth.get_transaction_count(account.address)
        
        transaction = self.contract.functions.updateDatasetTags(
            dataset_id,
            tags
        ).build_transaction({
            'from': account.address,
            'gas': 2000000,
            'nonce': nonce,
        })
        
        signed_txn = self.web3.eth.account.sign_transaction(
            transaction, account.private_key
        )
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)
    
    def set_dataset_access(self, dataset_id: int, is_public: bool, account) -> dict:
        """Set dataset access control"""
        nonce = self.web3.eth.get_transaction_count(account.address)
        
        transaction = self.contract.functions.setDatasetAccess(
            dataset_id,
            is_public
        ).build_transaction({
            'from': account.address,
            'gas': 2000000,
            'nonce': nonce,
        })
        
        signed_txn = self.web3.eth.account.sign_transaction(
            transaction, account.private_key
        )
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)
    
    def grant_access(self, dataset_id: int, user_address: str, account) -> dict:
        """Grant access to a user"""
        nonce = self.web3.eth.get_transaction_count(account.address)
        
        transaction = self.contract.functions.grantAccess(
            dataset_id,
            user_address
        ).build_transaction({
            'from': account.address,
            'gas': 2000000,
            'nonce': nonce,
        })
        
        signed_txn = self.web3.eth.account.sign_transaction(
            transaction, account.private_key
        )
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)
    
    def batch_list_datasets(self, metadata_hashes: list, prices: list,
                          descriptions: list, sizes: list, data_types: list,
                          account) -> dict:
        """Batch list multiple datasets"""
        nonce = self.web3.eth.get_transaction_count(account.address)
        
        transaction = self.contract.functions.batchListDatasets(
            metadata_hashes,
            prices,
            descriptions,
            sizes,
            data_types
        ).build_transaction({
            'from': account.address,
            'gas': 2000000,
            'nonce': nonce,
        })
        
        signed_txn = self.web3.eth.account.sign_transaction(
            transaction, account.private_key
        )
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)
    
    def set_subscription_price(self, dataset_id: int, price: int, account) -> dict:
        """Set subscription price for a dataset"""
        nonce = self.web3.eth.get_transaction_count(account.address)
        
        transaction = self.contract.functions.setSubscriptionPrice(
            dataset_id,
            price
        ).build_transaction({
            'from': account.address,
            'gas': 2000000,
            'nonce': nonce,
        })
        
        signed_txn = self.web3.eth.account.sign_transaction(
            transaction, account.private_key
        )
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)
    
    def subscribe_to_dataset(self, dataset_id: int, months: int, price: int, account) -> dict:
        """Subscribe to a dataset"""
        nonce = self.web3.eth.get_transaction_count(account.address)
        
        transaction = self.contract.functions.subscribe(
            dataset_id,
            months
        ).build_transaction({
            'from': account.address,
            'value': price * months,
            'gas': 2000000,
            'nonce': nonce,
        })
        
        signed_txn = self.web3.eth.account.sign_transaction(
            transaction, account.private_key
        )
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)
    
    def cancel_subscription(self, dataset_id: int, account) -> dict:
        """Cancel a dataset subscription"""
        nonce = self.web3.eth.get_transaction_count(account.address)
        
        transaction = self.contract.functions.cancelSubscription(
            dataset_id
        ).build_transaction({
            'from': account.address,
            'gas': 2000000,
            'nonce': nonce,
        })
        
        signed_txn = self.web3.eth.account.sign_transaction(
            transaction, account.private_key
        )
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)
    
    def check_subscription(self, dataset_id: int, user_address: str) -> bool:
        """Check if user has active subscription"""
        return self.contract.functions.checkSubscription(dataset_id, user_address).call() 