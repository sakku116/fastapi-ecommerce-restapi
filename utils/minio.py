from minio import Minio
import os
import inspect
from domain.model.base_model import MyBaseModel

from core.logging import logger


def ensureBuckets(minio: Minio) -> None:
    logger.info("Ensuring minio buckets")

    model_filenames = os.listdir("domain/model")
    logger.debug(f"found model files: {model_filenames}")
    for filename in model_filenames:
        if filename.endswith(".py") and filename.removesuffix(".py") not in [
            "__init__",
            "base_model",
        ]:
            module_path = __import__(
                f"domain.model.{filename[:-3]}", fromlist=[filename[:-3]]
            )
            for member_name, member in inspect.getmembers(module_path):
                if (
                    inspect.isclass(member)
                    and member_name.lower().endswith("model")
                    and member_name != "BaseModel"  # exclude pydantic.BaseModel
                ):
                    try:
                        bucket_name = member.getBucketName()
                        if not bucket_name:
                            continue

                        logger.info(f"\tEnsuring bucket for '{bucket_name}'")
                        if not minio.bucket_exists(bucket_name=bucket_name):
                            minio.make_bucket(bucket_name=bucket_name)
                            logger.info(f"\t\tcreated bucket: {bucket_name}")

                        else:
                            logger.info(f"\t\tbucket already exists: {bucket_name}")

                    except Exception as e:
                        logger.warning(f"\tFailed to create bucket: {e}")
