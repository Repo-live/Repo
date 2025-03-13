# Repo - Decentralized Dataset Marketplace

## Project Overview

Repo is a blockchain-based decentralized marketplace for dataset trading, enabling users to securely upload, trade, and manage datasets. The platform combines blockchain technology with IPFS distributed storage to ensure data security and reliability.

## Core Features

### 🗄️ Dataset Management

- Dataset upload and version control
- Data preview and quality assessment
- Comprehensive dataset analytics and statistics
- Support for CSV, JSON, and Parquet formats
- Dataset categorization and tagging system

### 💰 Trading Features

- One-time purchases and subscription models
- Batch operations for multiple datasets
- Platform fee system with smart contract guarantees
- Secure payment processing via Ethereum blockchain

### 🔒 Access Control & Security

- Fine-grained access control with public/private settings
- End-to-end encryption for sensitive data
- Ethereum wallet authentication
- IPFS distributed storage
- Data integrity verification

### 📊 Analytics & Quality

- Automated data quality assessment
- Statistical analysis and correlations
- Distribution analysis
- Quality recommendations
- Dataset comparison tools

## Technical Architecture

### Backend (Python)

```python
- FastAPI web framework
- Pandas & NumPy for data processing
- JWT authentication
- Pydantic for data validation
```

### Blockchain

```solidity
- Ethereum smart contracts (Solidity)
- Web3.py for blockchain interaction
- IPFS decentralized storage
```

## Getting Started

### Prerequisites

```bash
- Python 3.8+
- Node.js 12+
- IPFS daemon
- Ethereum node/testnet
```

### Installation

```bash
# Clone repository
cd repo

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Deploy smart contracts
truffle migrate --network <your-network>

# Start service
uvicorn src.market_api:app --reload
```

### Configuration

Required environment variables in `.env`:

```bash
WEB3_PROVIDER_URI=http://localhost:8545
CONTRACT_ADDRESS=<your-contract-address>
IPFS_HOST=localhost
IPFS_PORT=5001
SECRET_KEY=<your-secret-key>
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## API Reference

### Dataset Management

```python
# Upload dataset
POST /datasets
{
    "file": File,
    "metadata": {
        "price": float,
        "description": str,
        "data_type": str
    }
}

# Get dataset
GET /datasets/{dataset_id}

# Search datasets
GET /datasets/search?query=<query>&filters=<filters>

# Analyze dataset
POST /datasets/{dataset_id}/analyze

# Check quality
POST /datasets/{dataset_id}/quality
```

## Usage Examples

### Upload Dataset

```python
import requests

def upload_dataset(file_path, metadata):
    url = "http://localhost:8000/datasets"
    files = {"file": open(file_path, "rb")}
    response = requests.post(url, files=files, json=metadata)
    return response.json()
```

## Security Considerations

- Industry-standard encryption for all sensitive data
- Smart contracts audited for security vulnerabilities
- Access control enforced at both API and smart contract levels
- Regular security updates and vulnerability assessments
- Backup and recovery procedures for critical data

## Roadmap

- [ ] Dataset recommendation system
- [ ] Machine learning model training support
- [ ] Mobile application development
- [ ] Additional data format support
- [ ] Social features and community tools
- [ ] Advanced analytics capabilities

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/NewFeature`)
3. Commit changes (`git commit -m 'Add NewFeature'`)
4. Push to branch (`git push origin feature/NewFeature`)
5. Open Pull Request

## Contact

- [Twitter](https://x.com/AI__Repo)
