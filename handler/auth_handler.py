from fastapi import APIRouter, Depends

from domain.rest import auth_rest, generic_resp
from service import auth_service
from domain.dto import auth_dto
from core.dependencies import verifyToken

AuthRouter = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@AuthRouter.post(
    "/register",
    response_model=auth_rest.RegisterResp[auth_rest.BaseTokenResp],
    description="""
you may ask 'why there are duplicate access_token and refresh_token fields?'\n
well, fastapi oauth need `access_token` field in the root of the response,\n
also my mobile client GUY need it inside of the `data` field.
""",
)
def register(
    payload: auth_rest.RegisterReq = Depends(),
    auth_service: auth_service.AuthService = Depends(),
):
    resp = auth_service.register(payload=payload)
    resp.data = auth_rest.BaseTokenResp(
        access_token=resp.access_token,
        refresh_token=resp.refresh_token,
    )
    return resp


@AuthRouter.post(
    "/login",
    response_model=auth_rest.LoginResp[auth_rest.BaseTokenResp],
    description="""
you may ask 'why there are duplicate access_token and refresh_token fields?'\n
well, fastapi oauth need `access_token` field in the root of the response,\n
also my mobile client GUY need it inside of the `data` field
""",
)
def login(
    payload: auth_rest.LoginReq = Depends(),
    auth_service: auth_service.AuthService = Depends(),
):
    resp = auth_service.login(payload=payload)
    resp.data = auth_rest.BaseTokenResp(
        access_token=resp.access_token,
        refresh_token=resp.refresh_token,
    )
    return resp


@AuthRouter.post(
    "/refresh-token",
    response_model=auth_rest.RefreshTokenResp[auth_rest.BaseTokenResp],
    description="""
you may ask 'why there are duplicate access_token and refresh_token fields?'\n
well, fastapi oauth need `access_token` field in the root of the response,\n
also my mobile client GUY need it inside of the `data` field.
""",
)
def refresh_token(
    payload: auth_rest.RefreshTokenReq = Depends(),
    auth_service: auth_service.AuthService = Depends(),
):
    resp = auth_service.refreshToken(payload=payload)
    resp.data = auth_rest.BaseTokenResp(
        access_token=resp.access_token,
        refresh_token=resp.refresh_token,
    )
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


@AuthRouter.post("/forgot-password/send-otp", response_model=generic_resp.RespData)
async def forgot_password_send_otp(
    payload: auth_rest.SendEmailForgotPasswordOTPReq = Depends(),
    auth_service: auth_service.AuthService = Depends(),
):
    await auth_service.sendEmailForgotPasswordOTP(payload=payload)
    resp = generic_resp.RespData()
    resp.meta.message = "6-digit verification code has been sent to your email address."
    return resp


@AuthRouter.post(
    "/forgot-password/verify-otp",
    response_model=generic_resp.RespData[auth_rest.VerifyForgotPasswordOTPRespData],
)
def forgot_password_verify_otp(
    payload: auth_rest.VerifyForgotPasswordOTPReq = Depends(),
    auth_service: auth_service.AuthService = Depends(),
):
    data = auth_service.verifyForgotPasswordOTP(payload=payload)
    resp = generic_resp.RespData[auth_rest.VerifyForgotPasswordOTPRespData](data=data)
    resp.meta.message = "OTP verified successfully"
    return resp


@AuthRouter.post(
    "/forgot-password/change-password", response_model=generic_resp.RespData
)
def change_forgotten_password(
    payload: auth_rest.ChangeForgottenPasswordReq = Depends(),
    auth_service: auth_service.AuthService = Depends(),
):
    auth_service.changeForgottenPassword(payload=payload)
    resp = generic_resp.RespData()
    resp.meta.message = "Password changed successfully"
    return resp


@AuthRouter.post("/verify-email/send-otp", response_model=generic_resp.RespData)
async def verify_email_send_otp(
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
    auth_service: auth_service.AuthService = Depends(),
):
    await auth_service.sendVerifyEmailOTP(user_id=current_user.id)
    resp = generic_resp.RespData()
    resp.meta.message = "6-digit verification code has been sent to your email address."
    return resp


@AuthRouter.post("/verify-email/verify-otp", response_model=generic_resp.RespData)
def verify_email_verify_otp(
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
    payload: auth_rest.VerifyEmailOTPReq = Depends(),
    auth_service: auth_service.AuthService = Depends(),
):
    auth_service.verifyEmailOTP(user_id=current_user.id, payload=payload)
    resp = generic_resp.RespData()
    resp.meta.message = "Email verified successfully"
    return resp
