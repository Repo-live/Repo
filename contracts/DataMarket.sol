// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DataMarket {
    struct Dataset {
        address owner;
        string metadataHash;
        uint256 price;
        bool isActive;
        string description;
        uint256 size;
        string dataType;
    }
    
    mapping(uint256 => Dataset) public datasets;
    uint256 public datasetCount;
    
    mapping(address => uint256[]) public userDatasets;
    mapping(address => uint256[]) public userPurchases;
    uint256 public platformFee = 25; // 2.5% fee
    address public platformOwner;
    
    struct Review {
        address reviewer;
        uint8 rating;
        string comment;
        uint256 timestamp;
    }
    
    mapping(uint256 => Review[]) public datasetReviews;
    mapping(uint256 => uint256) public datasetTotalRatings;
    mapping(uint256 => uint256) public datasetReviewCount;
    
    struct Version {
        string metadataHash;
        string description;
        uint256 timestamp;
        string changeLog;
    }
    
    mapping(uint256 => Version[]) public datasetVersions;
    
    struct Category {
        string name;
        string description;
        bool isActive;
    }
    
    mapping(uint256 => Category) public categories;
    mapping(uint256 => uint256) public datasetCategories;
    mapping(uint256 => string[]) public datasetTags;
    uint256 public categoryCount;
    
    // Add access control structures
    struct AccessControl {
        bool isPublic;
        mapping(address => bool) allowedUsers;
        string[] allowedGroups;
    }
    
    mapping(uint256 => AccessControl) public datasetAccess;
    mapping(string => address[]) public userGroups;
    
    struct Subscription {
        uint256 startTime;
        uint256 endTime;
        uint256 price;
        bool isActive;
    }
    
    mapping(uint256 => mapping(address => Subscription)) public subscriptions;
    mapping(uint256 => uint256) public subscriptionPrices;
    
    event DatasetListed(uint256 indexed datasetId, address indexed owner, uint256 price);
    event DatasetPurchased(uint256 indexed datasetId, address indexed buyer, address indexed seller);
    event DatasetReviewed(uint256 indexed datasetId, address indexed reviewer, uint8 rating);
    event DatasetVersionAdded(uint256 indexed datasetId, uint256 versionNumber, string metadataHash);
    event CategoryAdded(uint256 indexed categoryId, string name);
    event DatasetCategoryUpdated(uint256 indexed datasetId, uint256 indexed categoryId);
    event DatasetTagsUpdated(uint256 indexed datasetId, string[] tags);
    event AccessControlUpdated(uint256 indexed datasetId, bool isPublic);
    event UserAccessGranted(uint256 indexed datasetId, address indexed user);
    event UserAccessRevoked(uint256 indexed datasetId, address indexed user);
    event SubscriptionCreated(uint256 indexed datasetId, address indexed subscriber, uint256 endTime);
    event SubscriptionCancelled(uint256 indexed datasetId, address indexed subscriber);
    
    constructor() {
        platformOwner = msg.sender;
    }
    
    function listDataset(
        string memory _metadataHash,
        uint256 _price,
        string memory _description,
        uint256 _size,
        string memory _dataType
    ) public {
        datasetCount++;
        datasets[datasetCount] = Dataset(
            msg.sender,
            _metadataHash,
            _price,
            true,
            _description,
            _size,
            _dataType
        );
        
        emit DatasetListed(datasetCount, msg.sender, _price);
        
        userDatasets[msg.sender].push(datasetCount);
    }
    
    function purchaseDataset(uint256 _datasetId) public payable {
        Dataset storage dataset = datasets[_datasetId];
        require(dataset.isActive, "Dataset is not active");
        require(msg.value >= dataset.price, "Insufficient payment");
        
        uint256 fee = (msg.value * platformFee) / 1000;
        uint256 sellerAmount = msg.value - fee;
        
        payable(dataset.owner).transfer(sellerAmount);
        payable(platformOwner).transfer(fee);
        
        userPurchases[msg.sender].push(_datasetId);
        emit DatasetPurchased(_datasetId, msg.sender, dataset.owner);
    }
    
    function getUserDatasets(address _user) public view returns (uint256[] memory) {
        return userDatasets[_user];
    }
    
    function getUserPurchases(address _user) public view returns (uint256[] memory) {
        return userPurchases[_user];
    }
    
    function updateDatasetPrice(uint256 _datasetId, uint256 _newPrice) public {
        require(datasets[_datasetId].owner == msg.sender, "Not the owner");
        datasets[_datasetId].price = _newPrice;
    }
    
    function deactivateDataset(uint256 _datasetId) public {
        require(datasets[_datasetId].owner == msg.sender, "Not the owner");
        datasets[_datasetId].isActive = false;
    }
    
    function reviewDataset(
        uint256 _datasetId,
        uint8 _rating,
        string memory _comment
    ) public {
        require(_rating >= 1 && _rating <= 5, "Rating must be between 1 and 5");
        require(datasets[_datasetId].isActive, "Dataset is not active");
        
        // Check if user has purchased the dataset
        bool hasPurchased = false;
        uint256[] memory purchases = userPurchases[msg.sender];
        for (uint i = 0; i < purchases.length; i++) {
            if (purchases[i] == _datasetId) {
                hasPurchased = true;
                break;
            }
        }
        require(hasPurchased, "Must purchase dataset before reviewing");
        
        // Add review
        datasetReviews[_datasetId].push(Review(
            msg.sender,
            _rating,
            _comment,
            block.timestamp
        ));
        
        // Update rating statistics
        datasetTotalRatings[_datasetId] += _rating;
        datasetReviewCount[_datasetId] += 1;
        
        emit DatasetReviewed(_datasetId, msg.sender, _rating);
    }
    
    function getDatasetRating(uint256 _datasetId) public view returns (uint256) {
        if (datasetReviewCount[_datasetId] == 0) {
            return 0;
        }
        return datasetTotalRatings[_datasetId] / datasetReviewCount[_datasetId];
    }
    
    function getDatasetReviews(uint256 _datasetId) public view returns (Review[] memory) {
        return datasetReviews[_datasetId];
    }
    
    function addDatasetVersion(
        uint256 _datasetId,
        string memory _metadataHash,
        string memory _description,
        string memory _changeLog
    ) public {
        require(datasets[_datasetId].owner == msg.sender, "Not the owner");
        require(datasets[_datasetId].isActive, "Dataset is not active");
        
        datasetVersions[_datasetId].push(Version(
            _metadataHash,
            _description,
            block.timestamp,
            _changeLog
        ));
        
        // Update current version in dataset
        datasets[_datasetId].metadataHash = _metadataHash;
        datasets[_datasetId].description = _description;
        
        emit DatasetVersionAdded(_datasetId, datasetVersions[_datasetId].length, _metadataHash);
    }
    
    function getDatasetVersions(uint256 _datasetId) public view returns (Version[] memory) {
        return datasetVersions[_datasetId];
    }
    
    function addCategory(string memory _name, string memory _description) public {
        require(msg.sender == platformOwner, "Only platform owner can add categories");
        categoryCount++;
        categories[categoryCount] = Category(_name, _description, true);
        emit CategoryAdded(categoryCount, _name);
    }
    
    function updateDatasetCategory(uint256 _datasetId, uint256 _categoryId) public {
        require(datasets[_datasetId].owner == msg.sender, "Not the owner");
        require(categories[_categoryId].isActive, "Invalid category");
        
        datasetCategories[_datasetId] = _categoryId;
        emit DatasetCategoryUpdated(_datasetId, _categoryId);
    }
    
    function updateDatasetTags(uint256 _datasetId, string[] memory _tags) public {
        require(datasets[_datasetId].owner == msg.sender, "Not the owner");
        datasetTags[_datasetId] = _tags;
        emit DatasetTagsUpdated(_datasetId, _tags);
    }
    
    function setDatasetAccess(uint256 _datasetId, bool _isPublic) public {
        require(datasets[_datasetId].owner == msg.sender, "Not the owner");
        datasetAccess[_datasetId].isPublic = _isPublic;
        emit AccessControlUpdated(_datasetId, _isPublic);
    }
    
    function grantAccess(uint256 _datasetId, address _user) public {
        require(datasets[_datasetId].owner == msg.sender, "Not the owner");
        datasetAccess[_datasetId].allowedUsers[_user] = true;
        emit UserAccessGranted(_datasetId, _user);
    }
    
    function revokeAccess(uint256 _datasetId, address _user) public {
        require(datasets[_datasetId].owner == msg.sender, "Not the owner");
        datasetAccess[_datasetId].allowedUsers[_user] = false;
        emit UserAccessRevoked(_datasetId, _user);
    }
    
    function hasAccess(uint256 _datasetId, address _user) public view returns (bool) {
        if (datasets[_datasetId].owner == _user) return true;
        if (datasetAccess[_datasetId].isPublic) return true;
        return datasetAccess[_datasetId].allowedUsers[_user];
    }
    
    // Add batch operations
    function batchListDatasets(
        string[] memory _metadataHashes,
        uint256[] memory _prices,
        string[] memory _descriptions,
        uint256[] memory _sizes,
        string[] memory _dataTypes
    ) public {
        require(_metadataHashes.length == _prices.length, "Arrays length mismatch");
        
        for (uint i = 0; i < _metadataHashes.length; i++) {
            listDataset(
                _metadataHashes[i],
                _prices[i],
                _descriptions[i],
                _sizes[i],
                _dataTypes[i]
            );
        }
    }
    
    function setSubscriptionPrice(uint256 _datasetId, uint256 _price) public {
        require(datasets[_datasetId].owner == msg.sender, "Not the owner");
        subscriptionPrices[_datasetId] = _price;
    }
    
    function subscribe(uint256 _datasetId, uint256 _months) public payable {
        require(datasets[_datasetId].isActive, "Dataset is not active");
        uint256 price = subscriptionPrices[_datasetId];
        require(price > 0, "Subscription not available");
        require(msg.value >= price * _months, "Insufficient payment");
        
        uint256 endTime = block.timestamp + (_months * 30 days);
        
        subscriptions[_datasetId][msg.sender] = Subscription(
            block.timestamp,
            endTime,
            price,
            true
        );
        
        // Transfer payment
        uint256 fee = (msg.value * platformFee) / 1000;
        uint256 sellerAmount = msg.value - fee;
        payable(datasets[_datasetId].owner).transfer(sellerAmount);
        payable(platformOwner).transfer(fee);
        
        emit SubscriptionCreated(_datasetId, msg.sender, endTime);
    }
    
    function cancelSubscription(uint256 _datasetId) public {
        require(subscriptions[_datasetId][msg.sender].isActive, "No active subscription");
        subscriptions[_datasetId][msg.sender].isActive = false;
        emit SubscriptionCancelled(_datasetId, msg.sender);
    }
    
    function checkSubscription(uint256 _datasetId, address _user) public view returns (bool) {
        Subscription memory sub = subscriptions[_datasetId][_user];
        return sub.isActive && block.timestamp <= sub.endTime;
    }
} 