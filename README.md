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

### Prerequisites

- Python 3.9+
- MongoDB server
- MinIO server or S3-compatible storage

### Installation

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

    Create a `.env` file. see [config/env.py](./config/env.py) file for env variable examples.

4. **Run the Application**:

    ```bash
    python main.py
    ```

    The API will be accessible at `http://localhost:8000`.

5. **Run the Application With Specific Options**

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