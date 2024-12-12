from fastapi import Depends

from core.exceptions.http import CustomHttpException
from core.logging import logger
from domain.rest import category_rest
from domain.model import category_model
from config.minio import getMinioClient
from repository import category_repo
from utils import helper
from minio import Minio


class CategoryService:
    def __init__(
        self,
        category_repo: category_repo.CategoryRepo = Depends(),
        minio_client: Minio = Depends(getMinioClient),
    ):
        self.category_repo = category_repo
        self.minio_client = minio_client

    def getList(
        self, query: category_rest.GetCategoryListReq
    ) -> tuple[list[category_rest.GetCategoryListRespDataItem], int]:
        sort_order = -1 if query.sort_order == "desc" else 1
        categories, count = self.category_repo.getList(
            query=query.query,
            query_by=query.query_by,
            sort_by=query.sort_by,
            sort_order=sort_order,
            skip=helper.generateSkip(query.page, query.limit),
            limit=query.limit,
            do_count=True,
        )

        result = []
        for category in categories:
            res_item = category_rest.GetCategoryListRespDataItem(
                **category.model_dump()
            )
            result.append(res_item)

        return result, count

    def createCategory(
        self, payload: category_rest.CreateCategoryReq, curr_user_id: str
    ) -> category_rest.CreateCategoryRespData:
        # check if name is already exist
        existing_category = self.category_repo.getByName(name=payload.name.lower())
        if existing_category:
            exc = CustomHttpException(
                status_code=400,
                message="Category already exist",
            )
            logger.error(exc)
            raise exc

        # upload image if any
        category_img = None
        if payload.img and payload.img.filename:
            if not helper.isImage(payload.img.filename):
                exc = CustomHttpException(
                    status_code=400,
                    message="File is not an image",
                )
                logger.error(exc)
                raise exc

            category_img = f"{helper.generateUUID4()}-{payload.img.filename}"
            try:
                self.minio_client.put_object(
                    bucket_name=category_model.CategoryModel.getBucketName(),
                    object_name=category_img,
                    data=payload.img.file,
                    length=payload.img.size or 0,
                    content_type=helper.getMimeType(payload.img.filename),
                )
            except Exception as e:
                exc = CustomHttpException(
                    status_code=500, message="Failed to store image", detail=str(e)
                )
                logger.error(exc)
                raise exc

        # create
        time_now = helper.timeNow()
        new_category = category_model.CategoryModel(
            id=helper.generateUUID4(),
            created_at=time_now,
            updated_at=time_now,
            created_by=curr_user_id,
            name=payload.name.lower(),
            description=payload.description,
            img=category_img,
        )
        self.category_repo.create(category=new_category)

        new_category.urlizeMinioFields(minio_client=self.minio_client)
        return category_rest.CreateCategoryRespData(**new_category.model_dump())
