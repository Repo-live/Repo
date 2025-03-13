from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Optional
from .blockchain_manager import BlockchainManager
from .data_manager import DataManager
from .auth import Auth, oauth2_scheme
from .config import settings
import os
from .analytics import DatasetAnalytics
from .quality_checker import QualityChecker

app = FastAPI()

class DatasetListing(BaseModel):
    price: float
    description: str
    data_type: str
    metadata: dict

class ReviewRequest(BaseModel):
    rating: int
    comment: str

class VersionUpdate(BaseModel):
    metadata_hash: str
    description: str
    changelog: str

class CategoryUpdate(BaseModel):
    category_id: int

class TagsUpdate(BaseModel):
    tags: list[str]

class AccessControlUpdate(BaseModel):
    is_public: bool

class BatchDatasetListing(BaseModel):
    datasets: list[DatasetListing]

class SearchFilters(BaseModel):
    data_type: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    owner: Optional[str] = None

class SubscriptionRequest(BaseModel):
    months: int
    price_per_month: int

class SubscriptionPriceUpdate(BaseModel):
    price: int

auth = Auth()

analytics = DatasetAnalytics()
quality_checker = QualityChecker()

@app.post("/datasets")
async def create_dataset(
    file: UploadFile,
    listing: DatasetListing
):
    try:
        # Upload to IPFS
        metadata_hash = data_manager.upload_dataset(
            file.file,
            listing.metadata
        )
        
        # List on blockchain
        tx_receipt = blockchain_manager.list_dataset(
            metadata_hash,
            listing.price,
            listing.description,
            file.size,
            listing.data_type,
            account
        )
        
        return {
            "status": "success",
            "metadata_hash": metadata_hash,
            "transaction_hash": tx_receipt['transactionHash'].hex()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: int):
    try:
        dataset = blockchain_manager.contract.functions.datasets(dataset_id).call()
        return {
            "owner": dataset[0],
            "metadata_hash": dataset[1],
            "price": dataset[2],
            "is_active": dataset[3],
            "description": dataset[4],
            "size": dataset[5],
            "data_type": dataset[6]
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail="Dataset not found")

@app.post("/login")
async def login(username: str, password: str):
    # Here you would verify the user credentials
    # For demo purposes, we'll create a simple token
    access_token = auth.create_access_token(
        data={"sub": username}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/user/datasets")
async def get_user_datasets(token: str = Depends(oauth2_scheme)):
    user_data = auth.verify_token(token)
    user_address = user_data["sub"]
    datasets = blockchain_manager.contract.functions.getUserDatasets(user_address).call()
    return {"datasets": datasets}

@app.post("/datasets/{dataset_id}/purchase")
async def purchase_dataset(
    dataset_id: int,
    token: str = Depends(oauth2_scheme)
):
    user_data = auth.verify_token(token)
    try:
        tx_receipt = blockchain_manager.purchase_dataset(
            dataset_id,
            account
        )
        return {
            "status": "success",
            "transaction_hash": tx_receipt['transactionHash'].hex()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/datasets/{dataset_id}/price")
async def update_dataset_price(
    dataset_id: int,
    new_price: float,
    token: str = Depends(oauth2_scheme)
):
    user_data = auth.verify_token(token)
    try:
        tx_receipt = blockchain_manager.update_dataset_price(
            dataset_id,
            new_price,
            account
        )
        return {
            "status": "success",
            "transaction_hash": tx_receipt['transactionHash'].hex()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/datasets/{dataset_id}/review")
async def review_dataset(
    dataset_id: int,
    review: ReviewRequest,
    token: str = Depends(oauth2_scheme)
):
    user_data = auth.verify_token(token)
    try:
        tx_receipt = blockchain_manager.review_dataset(
            dataset_id,
            review.rating,
            review.comment,
            account
        )
        return {
            "status": "success",
            "transaction_hash": tx_receipt['transactionHash'].hex()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/datasets/{dataset_id}/reviews")
async def get_dataset_reviews(dataset_id: int):
    try:
        reviews = blockchain_manager.contract.functions.getDatasetReviews(dataset_id).call()
        rating = blockchain_manager.contract.functions.getDatasetRating(dataset_id).call()
        return {
            "rating": rating,
            "reviews": [
                {
                    "reviewer": review[0],
                    "rating": review[1],
                    "comment": review[2],
                    "timestamp": review[3]
                }
                for review in reviews
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail="Dataset not found")

@app.post("/auth/ethereum")
async def ethereum_auth(address: str, signature: str, message: str):
    """Authenticate using Ethereum wallet"""
    if auth.verify_ethereum_signature(message, signature, address):
        access_token = auth.create_access_token(
            data={"sub": address, "type": "ethereum"}
        )
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid signature"
    )

@app.post("/datasets/preview")
async def preview_dataset(
    file: UploadFile,
    max_rows: Optional[int] = 10
):
    try:
        # Save uploaded file temporarily
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Generate preview
        preview = data_manager.generate_preview(temp_path, max_rows)
        
        # Clean up
        os.remove(temp_path)
        
        return preview
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/datasets/encrypted")
async def create_encrypted_dataset(
    file: UploadFile,
    listing: DatasetListing,
    password: str
):
    try:
        # Save uploaded file temporarily
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Upload encrypted dataset
        upload_result = data_manager.upload_dataset(
            temp_path,
            listing.metadata,
            password
        )
        
        # Clean up
        os.remove(temp_path)
        
        # List on blockchain
        tx_receipt = blockchain_manager.list_dataset(
            upload_result['metadata_hash'],
            listing.price,
            listing.description,
            file.size,
            listing.data_type,
            account
        )
        
        return {
            "status": "success",
            "metadata_hash": upload_result['metadata_hash'],
            "transaction_hash": tx_receipt['transactionHash'].hex()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/datasets/{dataset_id}/versions")
async def add_dataset_version(
    dataset_id: int,
    version: VersionUpdate,
    token: str = Depends(oauth2_scheme)
):
    user_data = auth.verify_token(token)
    try:
        tx_receipt = blockchain_manager.add_dataset_version(
            dataset_id,
            version.metadata_hash,
            version.description,
            version.changelog,
            account
        )
        return {
            "status": "success",
            "transaction_hash": tx_receipt['transactionHash'].hex()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/datasets/{dataset_id}/versions")
async def get_dataset_versions(dataset_id: int):
    try:
        versions = blockchain_manager.get_dataset_versions(dataset_id)
        return {"versions": versions}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Dataset not found")

@app.put("/datasets/{dataset_id}/category")
async def update_dataset_category(
    dataset_id: int,
    category: CategoryUpdate,
    token: str = Depends(oauth2_scheme)
):
    user_data = auth.verify_token(token)
    try:
        tx_receipt = blockchain_manager.update_dataset_category(
            dataset_id,
            category.category_id,
            account
        )
        return {
            "status": "success",
            "transaction_hash": tx_receipt['transactionHash'].hex()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/datasets/{dataset_id}/tags")
async def update_dataset_tags(
    dataset_id: int,
    tags_update: TagsUpdate,
    token: str = Depends(oauth2_scheme)
):
    user_data = auth.verify_token(token)
    try:
        tx_receipt = blockchain_manager.update_dataset_tags(
            dataset_id,
            tags_update.tags,
            account
        )
        return {
            "status": "success",
            "transaction_hash": tx_receipt['transactionHash'].hex()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/datasets/{dataset_id}/access")
async def update_dataset_access(
    dataset_id: int,
    access: AccessControlUpdate,
    token: str = Depends(oauth2_scheme)
):
    user_data = auth.verify_token(token)
    try:
        tx_receipt = blockchain_manager.set_dataset_access(
            dataset_id,
            access.is_public,
            account
        )
        return {
            "status": "success",
            "transaction_hash": tx_receipt['transactionHash'].hex()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/datasets/{dataset_id}/grant/{user_address}")
async def grant_dataset_access(
    dataset_id: int,
    user_address: str,
    token: str = Depends(oauth2_scheme)
):
    user_data = auth.verify_token(token)
    try:
        tx_receipt = blockchain_manager.grant_access(
            dataset_id,
            user_address,
            account
        )
        return {
            "status": "success",
            "transaction_hash": tx_receipt['transactionHash'].hex()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/datasets/batch")
async def batch_create_datasets(
    listings: BatchDatasetListing,
    token: str = Depends(oauth2_scheme)
):
    user_data = auth.verify_token(token)
    try:
        metadata_hashes = []
        prices = []
        descriptions = []
        sizes = []
        data_types = []
        
        for listing in listings.datasets:
            metadata_hashes.append(listing.metadata_hash)
            prices.append(listing.price)
            descriptions.append(listing.description)
            sizes.append(listing.size)
            data_types.append(listing.data_type)
        
        tx_receipt = blockchain_manager.batch_list_datasets(
            metadata_hashes,
            prices,
            descriptions,
            sizes,
            data_types,
            account
        )
        
        return {
            "status": "success",
            "transaction_hash": tx_receipt['transactionHash'].hex()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/datasets/search")
async def search_datasets(
    query: Optional[str] = None,
    filters: Optional[SearchFilters] = None
):
    try:
        results = data_manager.search_datasets(
            query,
            filters.dict() if filters else None
        )
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/datasets/{dataset_id}/analyze")
async def analyze_dataset(dataset_id: int, token: str = Depends(oauth2_scheme)):
    user_data = auth.verify_token(token)
    try:
        # Get dataset
        dataset = blockchain_manager.contract.functions.datasets(dataset_id).call()
        metadata = data_manager.retrieve_dataset(dataset[1])
        
        # Analyze dataset
        analysis_results = analytics.analyze_dataset(metadata[0])
        return analysis_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/datasets/{dataset_id}/quality")
async def check_dataset_quality(dataset_id: int, token: str = Depends(oauth2_scheme)):
    user_data = auth.verify_token(token)
    try:
        # Get dataset
        dataset = blockchain_manager.contract.functions.datasets(dataset_id).call()
        file_path, metadata = data_manager.retrieve_dataset(dataset[1])
        
        # Check quality
        quality_results = quality_checker.evaluate_quality(file_path, metadata)
        return quality_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/datasets/{dataset_id}/subscription-price")
async def set_subscription_price(
    dataset_id: int,
    price_update: SubscriptionPriceUpdate,
    token: str = Depends(oauth2_scheme)
):
    user_data = auth.verify_token(token)
    try:
        tx_receipt = blockchain_manager.set_subscription_price(
            dataset_id,
            price_update.price,
            account
        )
        return {
            "status": "success",
            "transaction_hash": tx_receipt['transactionHash'].hex()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/datasets/{dataset_id}/subscribe")
async def subscribe_to_dataset(
    dataset_id: int,
    subscription: SubscriptionRequest,
    token: str = Depends(oauth2_scheme)
):
    user_data = auth.verify_token(token)
    try:
        tx_receipt = blockchain_manager.subscribe_to_dataset(
            dataset_id,
            subscription.months,
            subscription.price_per_month,
            account
        )
        return {
            "status": "success",
            "transaction_hash": tx_receipt['transactionHash'].hex()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/datasets/{dataset_id}/cancel-subscription")
async def cancel_dataset_subscription(
    dataset_id: int,
    token: str = Depends(oauth2_scheme)
):
    user_data = auth.verify_token(token)
    try:
        tx_receipt = blockchain_manager.cancel_subscription(
            dataset_id,
            account
        )
        return {
            "status": "success",
            "transaction_hash": tx_receipt['transactionHash'].hex()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/datasets/{dataset_id}/check-subscription/{user_address}")
async def check_dataset_subscription(dataset_id: int, user_address: str):
    try:
        has_subscription = blockchain_manager.check_subscription(dataset_id, user_address)
        return {"has_subscription": has_subscription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 