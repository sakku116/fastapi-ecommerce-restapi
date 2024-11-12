from minio import Minio

from config.env import Env


def getMinioClient():
    return Minio(
        Env.MINIO_ENDPOINT,
        access_key=Env.MINIO_ACCESS_KEY,
        secret_key=Env.MINIO_SECRET_KEY,
        secure=False,
    )