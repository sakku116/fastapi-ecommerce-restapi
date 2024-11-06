from fastapi import Request, Response
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware


class JsonableRespEncoderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if isinstance(response, BaseModel):
            response = Response(
                content=response.model_dump(mode="json"), media_type="application/json"
            )

        return response
