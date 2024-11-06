from fastapi import APIRouter, Depends

from domain.rest import auth_rest, generic_resp
from service import auth_service

AuthRouter = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@AuthRouter.post("/register", response_model=auth_rest.RegisterResp)
def register(
    payload: auth_rest.RegisterReq = Depends(),
    auth_service: auth_service.AuthService = Depends(),
):
    resp = auth_service.register(payload=payload)
    return resp


@AuthRouter.post("/login", response_model=auth_rest.LoginResp)
def login(
    payload: auth_rest.LoginReq = Depends(),
    auth_service: auth_service.AuthService = Depends(),
):
    resp = auth_service.login(payload=payload)
    return resp


@AuthRouter.post("/refresh-token", response_model=auth_rest.RefreshTokenResp)
def refresh_token(
    payload: auth_rest.RefreshTokenReq = Depends(),
    auth_service: auth_service.AuthService = Depends(),
):
    resp = auth_service.refreshToken(payload=payload)
    return resp


@AuthRouter.post(
    "/check-token", response_model=generic_resp.RespData[auth_rest.CheckTokenRespData]
)
def check_token(
    payload: auth_rest.CheckTokenReq = Depends(),
    auth_service: auth_service.AuthService = Depends(),
):
    resp = auth_service.checkToken(payload=payload)
    return generic_resp.RespData[auth_rest.CheckTokenRespData](data=resp)
