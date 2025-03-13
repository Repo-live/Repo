import ipfs_api
import hashlib
import json
import pandas as pd
from typing import Dict, Any, Optional
from .encryption import DataEncryption

class DataManager:
    def __init__(self, ipfs_node):
        self.ipfs = ipfs_api.connect(ipfs_node)
        self.encryption = DataEncryption()
    
    def upload_dataset(self, file_path: str, metadata: Dict[str, Any], password: Optional[str] = None) -> Dict[str, Any]:
        # Calculate file hash
        file_hash = self._calculate_file_hash(file_path)
        
        # Encrypt file if password is provided
        if password:
            encrypted_file_path, salt = self.encryption.encrypt_file(file_path, password)
            ipfs_hash = self.ipfs.add(encrypted_file_path)['Hash']
            metadata['encrypted'] = True
            metadata['salt'] = salt.hex()
        else:
            ipfs_hash = self.ipfs.add(file_path)['Hash']
            metadata['encrypted'] = False
        
        # Create metadata
        metadata_obj = {
            'file_hash': file_hash,
            'ipfs_hash': ipfs_hash,
            'metadata': metadata
        }
        
        # Upload metadata to IPFS
        metadata_hash = self.ipfs.add_json(metadata_obj)
        
        return {
            'metadata_hash': metadata_hash,
            'ipfs_hash': ipfs_hash,
            'file_hash': file_hash
        }
    
    def retrieve_dataset(self, metadata_hash: str, password: Optional[str] = None) -> tuple:
        metadata = self.ipfs.get_json(metadata_hash)
        dataset_path = self.ipfs.get(metadata['ipfs_hash'])
        
        if metadata.get('encrypted', False) and password:
            salt = bytes.fromhex(metadata['salt'])
            dataset_path = self.encryption.decrypt_file(dataset_path, password, salt)
            
        return dataset_path, metadata
    
    def generate_preview(self, file_path: str, max_rows: int = 10) -> Dict[str, Any]:
        """Generate a preview of the dataset"""
        try:
            # Determine file type and read accordingly
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, nrows=max_rows)
            elif file_path.endswith('.json'):
                df = pd.read_json(file_path)[:max_rows]
            elif file_path.endswith('.parquet'):
                df = pd.read_parquet(file_path)[:max_rows]
            else:
                raise ValueError("Unsupported file format")
            
            preview = {
                'columns': df.columns.tolist(),
                'data': df.to_dict('records'),
                'total_rows': len(df),
                'preview_rows': min(max_rows, len(df)),
                'dtypes': df.dtypes.astype(str).to_dict()
            }
            
            # Add basic statistics
            preview['statistics'] = {
                'numeric_columns': df.select_dtypes(include=['int64', 'float64']).describe().to_dict(),
                'missing_values': df.isnull().sum().to_dict()
            }
            
            return preview
            
        except Exception as e:
            raise ValueError(f"Error generating preview: {str(e)}")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def search_datasets(self, query: str, filters: dict = None) -> list:
        """Search datasets based on query and filters"""
        try:
            # Get all datasets
            datasets = []
            for i in range(1, self.blockchain_manager.contract.functions.datasetCount().call() + 1):
                dataset = self.blockchain_manager.contract.functions.datasets(i).call()
                if dataset[3]:  # if active
                    metadata = self.ipfs.get_json(dataset[1])
                    dataset_info = {
                        'id': i,
                        'owner': dataset[0],
                        'price': dataset[2],
                        'description': dataset[4],
                        'size': dataset[5],
                        'data_type': dataset[6],
                        'metadata': metadata['metadata']
                    }
                    datasets.append(dataset_info)
            
            # Apply search query
            if query:
                query = query.lower()
                datasets = [
                    d for d in datasets
                    if query in d['description'].lower()
                    or query in d['data_type'].lower()
                    or any(query in str(v).lower() for v in d['metadata'].values())
                ]
            
            # Apply filters
            if filters:
                if 'data_type' in filters:
                    datasets = [d for d in datasets if d['data_type'] == filters['data_type']]
                if 'min_price' in filters:
                    datasets = [d for d in datasets if d['price'] >= filters['min_price']]
                if 'max_price' in filters:
                    datasets = [d for d in datasets if d['price'] <= filters['max_price']]
                if 'owner' in filters:
                    datasets = [d for d in datasets if d['owner'] == filters['owner']]
            
            return datasets
            
        except Exception as e:
            raise ValueError(f"Error searching datasets: {str(e)}") 