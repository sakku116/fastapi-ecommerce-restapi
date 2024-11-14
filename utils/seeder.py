from config.mongodb import getMongoDB
from domain.model import user_model, product_model, category_model
from repository import user_repo, product_repo, category_repo
from utils import bcrypt as bcrypt_utils
from config.env import Env
import requests
from core.logging import logger
from utils import helper


def seedInitialUsers(user_repo: user_repo.UserRepo):
    logger.info("Seeding initial users")

    users: list[user_model.UserModel] = []
    time_now = helper.timeNowEpoch()
    if Env.INITIAL_CUSTOMER_USER_USERNAME and Env.INITIAL_CUSTOMER_USER_PASSWORD:
        users.append(
            user_model.UserModel(
                id=helper.generateUUID4(),
                created_at=time_now,
                fullname=Env.INITIAL_CUSTOMER_USER_USERNAME.title().replace("_", " "),
                username=Env.INITIAL_CUSTOMER_USER_USERNAME,
                email=f"{Env.INITIAL_CUSTOMER_USER_USERNAME}@gmail.com",
                password=bcrypt_utils.hashPassword(Env.INITIAL_CUSTOMER_USER_PASSWORD),
                role="customer",
            )
        )

    if Env.INITIAL_SELLER_USER_USERNAME and Env.INITIAL_SELLER_USER_PASSWORD:
        users.append(
            user_model.UserModel(
                id=helper.generateUUID4(),
                created_at=time_now,
                fullname=Env.INITIAL_SELLER_USER_USERNAME.title().replace("_", " "),
                username=Env.INITIAL_SELLER_USER_USERNAME,
                email=f"{Env.INITIAL_SELLER_USER_USERNAME}@gmail.com",
                password=bcrypt_utils.hashPassword(Env.INITIAL_SELLER_USER_PASSWORD),
                role="seller",
            )
        )

    if Env.INITIAL_ADMIN_USER_USERNAME and Env.INITIAL_ADMIN_USER_PASSWORD:
        users.append(
            user_model.UserModel(
                id=helper.generateUUID4(),
                created_at=time_now,
                fullname=Env.INITIAL_ADMIN_USER_USERNAME.title().replace("_", " "),
                username=Env.INITIAL_ADMIN_USER_USERNAME,
                email=f"{Env.INITIAL_ADMIN_USER_USERNAME}@gmail.com",
                password=bcrypt_utils.hashPassword(Env.INITIAL_ADMIN_USER_PASSWORD),
                role="admin",
            )
        )

    for user in users:
        logger.info(f"Seeding initial user: {user.username}")
        existing = (
            user_repo.getByUsername(user.username)
            or user_repo.getByEmail(user.email)
            or None
        )
        if existing:
            logger.warning(f"User @{user.username} ({user.email}) already exists")
            continue

        user_repo.create(user)


def seedInitialCategories(
    category_repo: category_repo.CategoryRepo, user_repo: user_repo.UserRepo
):
    logger.info("Seeding initial categories")

    # get dummy categories
    try:
        url = "https://dummyjson.com/products/categories"
        response = requests.get(url, verify=False)
        response.raise_for_status()
    except Exception as e:
        logger.error(e)
        raise

    if response.status_code > 300:
        logger.error(f"Failed to get categories: {response.status_code}")
        raise

    raw_categories: list[dict] = None
    try:
        raw_categories = response.json()
    except Exception as e:
        logger.error(e)
        raise

    # get initial admin users
    admin_user = user_repo.getByUsername(username=Env.INITIAL_ADMIN_USER_USERNAME)
    if not admin_user:
        logger.error(f"Admin user not found: {Env.INITIAL_ADMIN_USER_USERNAME}")
        raise NotImplementedError(
            f"Admin user not found: {Env.INITIAL_ADMIN_USER_USERNAME}"
        )

    time_now = helper.timeNowEpoch()
    for category in raw_categories:
        if "name" not in category:
            logger.warning(f"raw category doesnt have name: {category}")
            continue

        if category_repo.getByName(name=category.get("name")):
            logger.warning(f"category already exists: {category.get('name')}")
            continue

        new_category = category_model.CategoryModel(
            id=helper.generateUUID4(),
            created_at=time_now,
            created_by=admin_user.id,
            name=category.get("name"),
        )

        category_repo.create(category=new_category)
        logger.info(f"initial category created: {new_category.name}")


def seedInitialProducts(
    product_repo: product_repo.ProductRepo,
    category_repo: category_repo.CategoryRepo,
    user_repo: user_repo.UserRepo,
):
    logger.info(f"Seeding initial products")

    # get dummy products
    try:
        url = "https://dummyjson.com/products"
        response = requests.get(url, verify=False)
        response.raise_for_status()
    except Exception as e:
        logger.error(e)
        raise

    if response.status_code > 300:
        logger.error(f"Failed to get products: {response.status_code}")
        raise

    raw_products: dict = None
    try:
        raw_products = response.json()
    except Exception as e:
        logger.error(e)
        raise

    seller_user = user_repo.getByUsername(username=Env.INITIAL_SELLER_USER_USERNAME)
    if not seller_user:
        logger.error(f"Seller user not found: {Env.INITIAL_SELLER_USER_USERNAME}")
        raise NotImplementedError(
            f"Seller user not found: {Env.INITIAL_SELLER_USER_USERNAME}"
        )

    products: list[dict] = raw_products.get("products") or []
    time_now = helper.timeNowEpoch()
    for product in products:
        if not product.get("title") and not product.get("sku"):
            logger.warning(f"raw product doesnt have title or sku: {product}")
            continue

        if product_repo.getByName(name=product.get("title")):
            logger.warning(f"product already exists: {product.get('title')}")
            continue

        # get category
        category = category_repo.getByName(name=product.get("category"))
        if not category:
            logger.warning(f"category not found: {product.get('category')}")

        new_product = product_model.ProductModel(
            id=helper.generateUUID4(),
            created_at=time_now,
            created_by=seller_user.id,
            category_id=category.id if category else None,
            name=product.get("title") or "",
            brand=product.get("brand") or "",
            description=product.get("description") or "",
            tags=product.get("tags") or [],
        )

        new_product_variant = product_model.ProductVariantModel(
            id=helper.generateUUID4(),
            created_at=time_now,
            created_by=seller_user.id,
            is_main=True,
            product_id=new_product.id,
            sku=product.get("sku") or "",
            stock=product.get("stock") or 0,
            price=product.get("price") or 0,
            discount_percentage=product.get("discountPercentage") or None,
            weight=product.get("weight") or 0,
            dimensions=product_model.ProductModel_Dimensions(
                height=product.get("dimensions", {}).get("height") or 0,
                width=product.get("dimensions", {}).get("width") or 0,
                depth=product.get("dimensions", {}).get("depth") or 0,
            ),
        )

        product_repo.create(product=new_product)
        product_repo.createVariant(product_variant=new_product_variant)
        logger.info(f"initial product created: {new_product.name}")
