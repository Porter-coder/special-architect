"""
Error Utilities

Handles error mapping, Chinese error messages, and consistent error responses.
"""

from typing import Dict, Optional, Any
import openai


# Error message mappings (English -> Chinese)
ERROR_MESSAGES = {
    # OpenAI SDK errors
    "API key not provided": "API 密钥未提供",
    "Invalid API key": "API 密钥无效",
    "Rate limit exceeded": "请求频率过高，请稍后重试",
    "Service unavailable": "AI 服务暂时不可用",
    "Invalid request": "请求格式无效",
    "Content too long": "内容长度超过限制",
    "Unsupported model": "不支持的模型",
    "Server error": "服务器内部错误",

    # File system errors
    "File not found": "文件不存在",
    "Permission denied": "权限被拒绝",
    "Disk full": "磁盘空间不足",
    "Directory not found": "目录不存在",

    # Validation errors
    "Invalid input": "输入无效",
    "Required field missing": "必填字段缺失",
    "Format error": "格式错误",

    # General errors
    "Unknown error": "未知错误",
    "Operation failed": "操作失败",
    "Timeout": "操作超时",
}


def get_error_message(error_key: str, default: str = "未知错误") -> str:
    """
    Get Chinese error message for a given error key.

    Args:
        error_key: Error key to look up
        default: Default message if key not found

    Returns:
        Chinese error message
    """
    return ERROR_MESSAGES.get(error_key, default)


def map_openai_error(error: Exception) -> str:
    """
    Map OpenAI SDK exceptions to Chinese error messages.

    Args:
        error: OpenAI exception

    Returns:
        Chinese error message
    """
    if isinstance(error, openai.APIError):
        error_str = str(error).lower()
        if "rate limit" in error_str:
            return get_error_message("Rate limit exceeded")
        elif "invalid api key" in error_str or "unauthorized" in error_str:
            return get_error_message("Invalid API key")
        elif "not found" in error_str:
            return get_error_message("Unsupported model")
        else:
            return get_error_message("Server error")

    elif isinstance(error, openai.RateLimitError):
        return get_error_message("Rate limit exceeded")

    elif isinstance(error, openai.APIStatusError):
        if error.status_code == 429:
            return get_error_message("Rate limit exceeded")
        elif error.status_code >= 500:
            return get_error_message("Service unavailable")
        elif error.status_code == 401:
            return get_error_message("Invalid API key")
        elif error.status_code == 404:
            return get_error_message("Unsupported model")
        else:
            return get_error_message("Invalid request")

    elif isinstance(error, openai.APIConnectionError):
        return get_error_message("Service unavailable")

    elif isinstance(error, openai.APITimeoutError):
        return get_error_message("Timeout")

    else:
        return get_error_message("Unknown error")


def create_error_response(message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a standardized error response.

    Args:
        message: Error message in Chinese
        details: Optional additional error details

    Returns:
        Standardized error response dictionary
    """
    response = {
        "success": False,
        "message": message
    }

    if details:
        response["details"] = details

    return response


def create_success_response(data: Any = None, message: str = "操作成功") -> Dict[str, Any]:
    """
    Create a standardized success response.

    Args:
        data: Response data
        message: Success message in Chinese

    Returns:
        Standardized success response dictionary
    """
    response = {
        "success": True,
        "message": message
    }

    if data is not None:
        response["data"] = data

    return response


def handle_service_error(service_name: str, error: Exception) -> str:
    """
    Handle service-specific errors and return appropriate Chinese message.

    Args:
        service_name: Name of the service that failed
        error: The exception that occurred

    Returns:
        Chinese error message
    """
    error_str = str(error).lower()

    # Handle file system errors
    if "file" in service_name.lower() or "directory" in service_name.lower():
        if "not found" in error_str:
            return get_error_message("File not found")
        elif "permission" in error_str:
            return get_error_message("Permission denied")
        elif "disk" in error_str or "space" in error_str:
            return get_error_message("Disk full")

    # Handle AI service errors
    elif "ai" in service_name.lower():
        return map_openai_error(error)

    # Generic service error
    return f"{service_name}服务错误: {get_error_message('Operation failed')}"


class ErrorContext:
    """
    Context manager for error handling with consistent Chinese messages.
    """

    def __init__(self, operation: str):
        self.operation = operation

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Log the original error for debugging
            print(f"{self.operation} 失败: {exc_val}")

            # Re-raise with Chinese message
            if hasattr(exc_val, 'chinese_message'):
                raise Exception(exc_val.chinese_message) from exc_val
            else:
                chinese_msg = handle_service_error(self.operation, exc_val)
                raise Exception(chinese_msg) from exc_val
