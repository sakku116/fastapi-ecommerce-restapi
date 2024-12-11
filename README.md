# E-Commerce REST API (Under Development)

A REST API backend for an e-commerce application built with **FastAPI**, **MongoDB**, and **MinIO**. This API enables product management, user authentication, product reviews, role-based access control, and more.

## Features

- **Product Management**: Endpoints to create, read, update, and delete products with support for variants (e.g., color, size).
- **Review System**: Users can submit reviews and ratings (up to 5 points) for products, and the API calculates average ratings.
- **Role-Based Access Control (RBAC)**: Role-specific access for `Customer`, `Seller`, and `Admin` roles.
- **User Authentication and OTP Verification**: Secure user authentication with JWT, including OTP-based email verification and password reset.
- **Refresh Tokens**: Support for refresh tokens to renew access tokens without requiring the user to log in again.
- **Categories**: Organize products into categories to improve discoverability.
- **Order Management**: Basic order handling for checkout and order history.
- **Object Storage**: Media uploads and storage with MinIO, compatible with Amazon S3.

## Tech Stack

- **Framework**: FastAPI
- **Database**: MongoDB
- **Object Storage**: MinIO (for media and file storage)
- **Authentication**: JWT & OTP for email verification, password reset, and refresh token

## Design and Client

- **Figma Design**: [https://www.figma.com/community/file/1282297701057617450](#)
- **Mobile Client Repository**: [https://github.com/ericwidhiantara/QuickMart](#)

## Getting Started

### How to run with Docker
1. **Clone the repository**:

    ```bash
    git clone https://github.com/sakku116/fastapi-ecommerce-restapi.git
    cd fastapi-ecommerce-restapi
    ```

2. **Configure environment variables**:

    Create a `.env` file. see [./.env.example](./.env.example) file for env variable examples.

3. **Run docker compose**
    Run docker compose command:
    ```
    docker compose up -d
    ```
    The API will be accessible at `http://localhost:8000` (if use default port)

### How to run manually
#### Prerequisites
- Python 3.9+
- MongoDB server
- MinIO server or S3-compatible storage

1. **Clone the repository**:

    ```bash
    git clone https://github.com/sakku116/fastapi-ecommerce-restapi.git
    cd fastapi-ecommerce-restapi
    ```

2. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

    >I recommend to use virtualenv or docker.

3. **Configure environment variables**:

    Create a `.env` file. see [./.env.example](./.env.example) file for env variable examples.

4. **Run the application**:

    ```bash
    python main.py
    ```

    The API will be accessible at `http://localhost:8000` (if use default port)

5. **Run the application with specific options**:

    To run the app with specific options, you can use the following command-line arguments:

    ```bash
    python main.py [arguments]
    ```

    Available Arguments:
    - `--ensure-indexes`: Ensures that the necessary indexes are created in the MongoDB database.
    - `--ensure-buckets`: Ensures that the necessary MinIO buckets are created for file storage.
    - `--seed-initial-users`: Seeds the database with initial users (e.g., admin, sellers, and customers) if these envs is filled up in `.env` file:
        - `INITIAL_CUSTOMER_USER_USERNAME`
        - `INITIAL_CUSTOMER_USER_PASSWORD`
        - `INITIAL_SELLER_USER_USERNAME`
        - `INITIAL_SELLER_USER_PASSWORD`
        - `INITIAL_ADMIN_USER_USERNAME`
        - `INITIAL_ADMIN_USER_PASSWORD`
    - `--seed-initial-categories`: Seeds the database with initial product categories.
    - `--seed-initial-products`: Seeds the database with initial products and product variants.

## **Model**: MyBaseModel
The `MyBaseModel` class is a base model that provides essential fields and functionality for other models. It includes private attributes, indexes, and support for tracking creation and update timestamps.

```python
class MyBaseModel(MinioUtil):
    _coll_name: ModelPrivateAttr = PrivateAttr("")

    _default_indexes: list[_MyBaseModel_Index] = [
        _MyBaseModel_Index(keys=[("id", 1)], unique=True)
    ]
    _custom_indexes: list[_MyBaseModel_Index] = []

    _default_int64_fields: list[str] = ["created_at", "updated_at"]
    _custom_int64_fields: list[str] = []

    id: str = ""
    created_at: int = 0
    updated_at: int = 0
    created_by: str = ""
    updated_by: str = ""

    def model_dump(self, **kwargs) -> dict:
        data = super().model_dump(**kwargs)
        for field in self._custom_int64_fields + self._default_int64_fields:
            if field in data:
                data[field] = Int64(data[field])
        return data

    @classmethod
    def getCollName(cls) -> str:
        return cls._coll_name.get_default()

    @classmethod
    def getDefaultIndexes(cls):
        return cls._default_indexes.get_default()

    @classmethod
    def getCustomIndexes(cls):
        return cls._custom_indexes.get_default()

    @classmethod
    def getDefaultInt64Fields(cls):
        return cls._default_int64_fields.get_default()

    @classmethod
    def getCustomInt64Fields(cls):
        return cls._custom_int64_fields.get_default()
```

### Private Attribute: _coll_name
The `_coll_name` attribute is a private attribute of type ModelPrivateAttr. It is used to define the collection name for models that inherit from MyBaseModel. This is primarily for internal use and ensures that each model has its corresponding collection name in MongoDB.

```python
class MyBaseModel(MinioUtil):
    _coll_name: ModelPrivateAttr = PrivateAttr("")
```

### Default and Custom Indexes
The `MyBaseModel` class defines default indexes for MongoDB collections, as well as custom indexes. Indexes will be ensured via `--ensure-indexes` argument when running the app. By default, it ensures a unique index on the id field:

```python
_default_indexes: list[_MyBaseModel_Index] = [
    _MyBaseModel_Index(keys=[("id", 1)], unique=True)
]
_custom_indexes: list[_MyBaseModel_Index] = []
```

### Default and Custom int64 Fields
This model also includes default fields like created_at and updated_at, which are typically represented as int64 for timestamp storage. You can define custom int64 fields as needed. The defined fields will be converted to `bson.int64.Int64` when `model_dump()` called:

```python
_default_int64_fields: list[str] = ["created_at", "updated_at"]
_custom_int64_fields: list[str] = []
```

### Default Model Fields
The model includes the following default fields:
```python
id: A unique identifier for the model.
created_at: A timestamp for when the document was created.
updated_at: A timestamp for when the document was last updated.
created_by: The user who created the document.
updated_by: The user who last updated the document.
```

### Minio Utility in MyBaseModel
`MyBaseModel` inherits from the `MinioUtil` class to take advantage of the utility functions that assist with file handlign and MinIO storage. The MinioUtil class adds several important features:

1. `_bucket_name`: This private attribute defines the name of the MinIO bucket that will be used for storing files related to the model. The bucket name can be created or ensured using the `--ensure-buckets` argument when running the app. This ensures that the bucket exists before storing files.

2. `_minio_fields`: This private attribute is a list of fields in the model user defined that are used to store file names.


3. `urlizeMinioFields`: This method is used to transform any fields defined in `_minio_fields` into full URLs pointing to the corresponding files in the MinIO storage. This allows easy access to files by their URLs.