STATUS_OK = 0
STATUS_NO_REQUIRED_HEADERS = 1000
STATUS_NO_REQUIRED_ARGS = 1001
STATUS_NO_REQUIRED_PARAMETER = 1002
STATUS_PARAMETER_INVALID = 1003
STATUS_NO_RESOURCE = 2000
STATUS_NEED_LOGIN = 3000
STATUS_CANNOT_LOGIN = 3001
STATUS_TOKEN_INVALID = 3002
STATUS_TOKEN_EXPIRED = 3003
STATUS_BODY_INVALID = 3004
STATUS_USER_ALREADY_REGISTERED = 3005
STATUS_DEVICE_ALREADY_BINDED = 3006
STATUS_USERNAME_PASSWORD_INVALID = 3007
STATUS_NO_ORDER_STATUS = 4000
STATUS_NO_VALUE_CARD_INFO = 4001
STATUS_METHOD_NOT_ALLOWED = 4005
STATUS_CANNOT_DECRYPT = 5001

MESSAGES = {
    STATUS_NO_REQUIRED_HEADERS: 'access token or version was not existed in request header',
    STATUS_NO_REQUIRED_ARGS: "no %s argument(s) in request",
    STATUS_NO_REQUIRED_PARAMETER: "no %s parameter(s) in request body",
    STATUS_PARAMETER_INVALID: 'the parameter of request is not valid',
    STATUS_NO_RESOURCE: 'The resource you required was not existed in system',
    STATUS_NEED_LOGIN: 'You need to login sytem first',
    STATUS_CANNOT_LOGIN: 'You cannot login sytem using code: %s',
    STATUS_TOKEN_INVALID: 'the access token in header was invalid',
    STATUS_TOKEN_EXPIRED: 'the access token in header was expired',
    STATUS_BODY_INVALID: 'the device body format is not valid',
    STATUS_USER_ALREADY_REGISTERED: 'the device or user already registered',
    STATUS_DEVICE_ALREADY_BINDED: 'the device or user already registered',
    STATUS_USERNAME_PASSWORD_INVALID: 'the username or password is invalid, please check them',
    STATUS_NO_ORDER_STATUS: 'status code is invalid in request',
    STATUS_METHOD_NOT_ALLOWED: 'the method not allowed in request',
    STATUS_NO_VALUE_CARD_INFO: 'value card info was not binding to the member',
    STATUS_CANNOT_DECRYPT: 'cannot decrypt the request things',
}
