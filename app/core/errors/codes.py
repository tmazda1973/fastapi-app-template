from enum import Enum

__all__ = [
    "ErrorCode",
    "ERROR_I18N_MAPPING",
]


class ErrorCode(str, Enum):
    """
    エラーコード
    """

    # 共通
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    BAD_REQUEST = "BAD_REQUEST"

    # ユーザー
    USER_LOGIN_FAILED = "USER_LOGIN_FAILED"
    USER_EMAIL_EXISTS = "USER_EMAIL_EXISTS"
    USER_EMAIL_NOT_FOUND = "USER_EMAIL_NOT_FOUND"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_INVALID_CREDENTIALS = "USER_INVALID_CREDENTIALS"
    USER_ACCOUNT_DISABLED = "USER_ACCOUNT_DISABLED"
    USER_UNVERIFIED = "USER_UNVERIFIED"
    USER_NOT_HAVE_INVITE_PERMISSION = "USER_NOT_HAVE_INVITE_PERMISSION"
    USER_CANNOT_BE_INVITED = "USER_CANNOT_BE_INVITED"

    # パスワード関連
    PASSWORD_CHANGE_SUCCESS = "PASSWORD_CHANGE_SUCCESS"
    PASSWORD_CHANGE_FAILED = "PASSWORD_CHANGE_FAILED"
    PASSWORD_RESET_EMAIL_SENT = "PASSWORD_RESET_EMAIL_SENT"
    PASSWORD_RESET_PROCESS_FAILED = "PASSWORD_RESET_PROCESS_FAILED"
    PASSWORD_RESET_SUCCESS = "PASSWORD_RESET_SUCCESS"
    PASSWORD_RESET_FAILED = "PASSWORD_RESET_FAILED"

    # 招待関連
    INVITE_SEND_SUCCESS = "INVITE_SEND_SUCCESS"
    INVITE_SEND_FAILED = "INVITE_SEND_FAILED"
    INVITE_TOKEN_INVALID = "INVITE_TOKEN_INVALID"
    INVITE_TOKEN_EXPIRED = "INVITE_TOKEN_EXPIRED"
    INVITE_TOKEN_MISMATCH = "INVITE_TOKEN_MISMATCH"
    INVITE_USER_NOT_FOUND = "INVITE_USER_NOT_FOUND"
    INVITE_USER_ALREADY_VERIFIED = "INVITE_USER_ALREADY_VERIFIED"
    INVITE_TOKEN_VERIFICATION_FAILED = "INVITE_TOKEN_VERIFICATION_FAILED"
    INVITE_ACCEPT_SUCCESS = "INVITE_ACCEPT_SUCCESS"
    INVITE_ACCEPT_FAILED = "INVITE_ACCEPT_FAILED"

    # ユーザー登録関連
    USER_REGISTER_SUCCESS = "USER_REGISTER_SUCCESS"
    USER_REGISTER_FAILED = "USER_REGISTER_FAILED"

    # 企業
    COMPANY_NOT_FOUND = "COMPANY_NOT_FOUND"

    # 企業サブグループ
    COMPANY_SUBGROUP_NOT_FOUND = "COMPANY_SUBGROUP_NOT_FOUND"


ERROR_I18N_MAPPING = {
    # 共通
    ErrorCode.INTERNAL_SERVER_ERROR: "message.errors.common.internal_server_error",
    ErrorCode.VALIDATION_ERROR: "message.errors.common.validation_error",
    ErrorCode.NOT_FOUND: "message.errors.common.not_found",
    ErrorCode.UNAUTHORIZED: "message.errors.common.unauthorized",
    ErrorCode.FORBIDDEN: "message.errors.common.forbidden",
    ErrorCode.BAD_REQUEST: "message.errors.common.bad_request",
    # 企業
    ErrorCode.COMPANY_NOT_FOUND: "message.errors.company.not_found",
    # 企業サブグループ
    ErrorCode.COMPANY_SUBGROUP_NOT_FOUND: "message.errors.company_subgroup.not_found",
    # ユーザー
    ErrorCode.USER_LOGIN_FAILED: "message.errors.user.login_failed",
    ErrorCode.USER_EMAIL_EXISTS: "message.errors.user.email_already_exists",
    ErrorCode.USER_EMAIL_NOT_FOUND: "message.errors.user.email_not_found",
    ErrorCode.USER_NOT_FOUND: "message.errors.user.not_found",
    ErrorCode.USER_INVALID_CREDENTIALS: "message.errors.user.invalid_credentials",
    ErrorCode.USER_ACCOUNT_DISABLED: "message.errors.user.account_disabled",
    ErrorCode.USER_UNVERIFIED: "message.errors.user.unverified",
    ErrorCode.USER_NOT_HAVE_INVITE_PERMISSION: "message.errors.user.not_have_invite_permission",
    ErrorCode.USER_CANNOT_BE_INVITED: "message.errors.user.cannot_be_invited",
    # パスワード関連
    ErrorCode.PASSWORD_CHANGE_SUCCESS: "message.success.password.change_success",
    ErrorCode.PASSWORD_CHANGE_FAILED: "message.errors.password.change_failed",
    ErrorCode.PASSWORD_RESET_EMAIL_SENT: "message.success.password.reset_email_sent",
    ErrorCode.PASSWORD_RESET_PROCESS_FAILED: "message.errors.password.reset_process_failed",
    ErrorCode.PASSWORD_RESET_SUCCESS: "message.success.password.reset_success",
    ErrorCode.PASSWORD_RESET_FAILED: "message.errors.password.reset_failed",
    # 招待関連
    ErrorCode.INVITE_SEND_SUCCESS: "message.success.invite.send_success",
    ErrorCode.INVITE_SEND_FAILED: "message.errors.invite.send_failed",
    ErrorCode.INVITE_TOKEN_INVALID: "message.errors.invite.token_invalid",
    ErrorCode.INVITE_TOKEN_EXPIRED: "message.errors.invite.token_expired",
    ErrorCode.INVITE_TOKEN_MISMATCH: "message.errors.invite.token_mismatch",
    ErrorCode.INVITE_USER_NOT_FOUND: "message.errors.invite.user_not_found",
    ErrorCode.INVITE_USER_ALREADY_VERIFIED: "message.errors.invite.user_already_verified",
    ErrorCode.INVITE_TOKEN_VERIFICATION_FAILED: "message.errors.invite.token_verification_failed",
    ErrorCode.INVITE_ACCEPT_SUCCESS: "message.success.invite.accept_success",
    ErrorCode.INVITE_ACCEPT_FAILED: "message.errors.invite.accept_failed",
    # ユーザー登録関連
    ErrorCode.USER_REGISTER_SUCCESS: "message.success.user.register_success",
    ErrorCode.USER_REGISTER_FAILED: "message.errors.user.register_failed",
}
