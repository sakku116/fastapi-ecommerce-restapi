from fastapi import Request
from fastapi.responses import JSONResponse

from core.exceptions.http import CustomHttpException
from domain.rest import generic_resp
from fastapi.exceptions import RequestValidationError
from typing import Union


async def customHttpExceptionHandler(request: Request, exc: CustomHttpException):
    return JSONResponse(
        status_code=exc.status_code,
        content=generic_resp.RespData[Union[dict, list, None]](
            meta=generic_resp.BaseResp_Meta(
                code=exc.status_code,
                error=True if exc.status_code >= 400 else False,
                message=exc.message,
                error_detail=exc.detail,
            )
        ).model_dump(),
    )


async def defaultHttpExceptionHandler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=generic_resp.RespData[Union[dict, list, None]](
            meta=generic_resp.BaseResp_Meta(
                code=500,
                error=True,
                message="something went wrong",
                error_detail=str(exc),
            )
        ).model_dump(),
    )


async def runTimeErrorHandler(request: Request, exc: RuntimeError):
    return JSONResponse(
        status_code=500,
        content=generic_resp.RespData[Union[dict, list, None]](
            meta=generic_resp.BaseResp_Meta(
                code=500,
                error=True,
                message="something went wrong",
                error_detail=str(exc),
            )
        ).model_dump(),
    )


async def reqValidationErrExceptionHandler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(
        status_code=422,
        content=generic_resp.RespData[Union[dict, list, None]](
            meta=generic_resp.BaseResp_Meta(
                code=422,
                error=True,
                message="request validation error",
                error_detail=exc.errors(),
            )
        ).model_dump(),
    )


async def notFoundErrHandler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content=generic_resp.RespData[Union[dict, list, None]](
            meta=generic_resp.BaseResp_Meta(
                code=404,
                error=True,
                message="not found",
                error_detail=str(exc),
            )
        ).model_dump(),
    )
