
class ErrorCode:
    SUCCESS = 0
    HTTP_SUCCESS = 200
    HTTP_UNAUTHORIZED = 401
    UNAUTHORIZED = 401
    HTTP_FORBIDDEN = 403
    HTTP_NOT_FOUND = 404
    HTTP_INTERNAL_SERVER_ERROR = 500
    
    AUTH_KEY_LIMIT_EXCEEDED = 20001
    AUTH_KEY_INVALID = 20002
    AUTH_KEY_EXPIRED = 20003
    AUTH_KEY_REQUIRED = 20004
    
    NOT_FOUND = 10005
    
    @staticmethod
    def to_message(code):
        if code == ErrorCode.SUCCESS:
            return '成功'
        elif code == ErrorCode.HTTP_UNAUTHORIZED:
            return '未授权'
        elif code == ErrorCode.HTTP_FORBIDDEN:
            return '禁止访问'
        elif code == ErrorCode.HTTP_NOT_FOUND:
            return '未找到'
        elif code == ErrorCode.HTTP_INTERNAL_SERVER_ERROR:
            return '服务器错误'
        elif code == ErrorCode.AUTH_KEY_LIMIT_EXCEEDED:
            return '密钥调用次数超过限制'
        elif code == ErrorCode.AUTH_KEY_INVALID:
            return '密钥无效'
        elif code == ErrorCode.AUTH_KEY_EXPIRED:
            return '密钥已过期'
        elif code == ErrorCode.AUTH_KEY_REQUIRED:
            return '需要密钥'
        elif code == ErrorCode.NOT_FOUND:
            return '未找到'
        else:
            return '未知错误'


error_code = ErrorCode()
