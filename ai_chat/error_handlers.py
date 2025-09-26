"""
AI聊天服务错误处理工具
提供统一的错误响应格式和错误码定义
"""

import json
import logging
from typing import Dict, Any, Optional, List
from django.http import JsonResponse
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

class ErrorCode:
    """错误码定义"""
    # 通用错误码 (1000-1999)
    INVALID_REQUEST_FORMAT = "1001"
    MISSING_REQUIRED_FIELD = "1002"
    INVALID_FIELD_TYPE = "1003"
    INVALID_FIELD_VALUE = "1004"
    VALIDATION_FAILED = "1005"

    # 图片相关错误 (2000-2999)
    IMAGE_UPLOAD_FAILED = "2001"
    IMAGE_FORMAT_UNSUPPORTED = "2002"
    IMAGE_SIZE_TOO_LARGE = "2003"
    IMAGE_PROCESSING_ERROR = "2004"
    IMAGE_NOT_FOUND = "2005"
    IMAGE_CACHE_EXPIRED = "2006"

    # AI服务错误 (3000-3999)
    AI_SERVICE_ERROR = "3001"
    AI_MODEL_ERROR = "3002"
    AI_TIMEOUT_ERROR = "3003"
    AI_RATE_LIMIT_ERROR = "3004"
    AI_INVALID_PARAMETER = "3005"

    # 系统错误 (4000-4999)
    INTERNAL_SERVER_ERROR = "4001"
    DATABASE_ERROR = "4002"
    CACHE_ERROR = "4003"
    EXTERNAL_SERVICE_ERROR = "4004"


class ErrorResponse:
    """统一错误响应格式"""

    @staticmethod
    def create_error_response(
        error_code: str,
        error_message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        field_name: Optional[str] = None,
        received_value: Optional[Any] = None
    ) -> JsonResponse:
        """
        创建统一的错误响应

        Args:
            error_code: 错误码
            error_message: 错误消息
            status_code: HTTP状态码
            details: 详细错误信息
            suggestion: 解决建议
            field_name: 错误字段名
            received_value: 接收到的值

        Returns:
            JsonResponse对象
        """
        response_data = {
            'success': False,
            'error': error_message,
            'error_code': error_code,
            'error_type': ErrorResponse._get_error_type(error_code)
        }

        if details:
            response_data['details'] = details

        if suggestion:
            response_data['suggestion'] = suggestion

        if field_name:
            response_data['field_name'] = field_name

        if received_value is not None:
            response_data['received_value'] = received_value

        return JsonResponse(response_data, status=status_code)

    @staticmethod
    def _get_error_type(error_code: str) -> str:
        """根据错误码获取错误类型"""
        code_prefix = error_code[:1]

        if code_prefix == '1':
            return 'validation_error'
        elif code_prefix == '2':
            return 'image_error'
        elif code_prefix == '3':
            return 'ai_service_error'
        elif code_prefix == '4':
            return 'system_error'
        else:
            return 'unknown_error'

    @staticmethod
    def validation_error(
        message: str,
        field_name: Optional[str] = None,
        expected_type: Optional[str] = None,
        received_type: Optional[str] = None,
        suggestion: Optional[str] = None
    ) -> JsonResponse:
        """验证错误响应"""
        details = {}
        if expected_type:
            details['expected_type'] = expected_type
        if received_type:
            details['received_type'] = received_type

        return ErrorResponse.create_error_response(
            error_code=ErrorCode.VALIDATION_FAILED,
            error_message=message,
            status_code=400,
            details=details,
            suggestion=suggestion,
            field_name=field_name
        )

    @staticmethod
    def missing_field_error(
        field_name: str,
        expected_type: str,
        suggestion: Optional[str] = None
    ) -> JsonResponse:
        """缺失必填字段错误"""
        return ErrorResponse.create_error_response(
            error_code=ErrorCode.MISSING_REQUIRED_FIELD,
            error_message=f'{field_name}字段不能为空',
            status_code=400,
            details={'expected_type': expected_type},
            suggestion=suggestion,
            field_name=field_name
        )

    @staticmethod
    def image_upload_error(
        message: str,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None
    ) -> JsonResponse:
        """图片上传错误"""
        return ErrorResponse.create_error_response(
            error_code=ErrorCode.IMAGE_UPLOAD_FAILED,
            error_message=message,
            status_code=400,
            details=details or {},
            suggestion=suggestion or '请检查图片格式和大小要求'
        )

    @staticmethod
    def ai_service_error(
        message: str,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        model_used: Optional[str] = None
    ) -> JsonResponse:
        """AI服务错误"""
        error_details = details or {}
        if model_used:
            error_details['model_used'] = model_used

        return ErrorResponse.create_error_response(
            error_code=ErrorCode.AI_SERVICE_ERROR,
            error_message=message,
            status_code=500,
            details=error_details,
            suggestion=suggestion or 'AI服务暂时不可用，请稍后重试'
        )

    @staticmethod
    def server_error(
        message: str = '服务器内部错误',
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[str] = None
    ) -> JsonResponse:
        """服务器内部错误"""
        error_details = details or {}
        if original_error and original_error != message:
            error_details['original_error'] = original_error

        return ErrorResponse.create_error_response(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            error_message=message,
            status_code=500,
            details=error_details,
            suggestion='服务器暂时不可用，请稍后重试'
        )


class RequestValidator:
    """请求验证器"""

    @staticmethod
    def validate_json_request(request) -> tuple[bool, Optional[Dict[str, Any]], Optional[JsonResponse]]:
        """验证JSON请求"""
        content_type = request.content_type or ''
        if not content_type.startswith('application/json'):
            error_response = ErrorResponse.create_error_response(
                error_code=ErrorCode.INVALID_REQUEST_FORMAT,
                error_message='Content-Type必须是application/json',
                status_code=400,
                details={'received_content_type': content_type},
                suggestion='请使用JSON格式发送请求数据'
            )
            return False, None, error_response

        try:
            data = json.loads(request.body)
            return True, data, None
        except json.JSONDecodeError as e:
            error_response = ErrorResponse.create_error_response(
                error_code=ErrorCode.INVALID_REQUEST_FORMAT,
                error_message='请求数据格式错误',
                status_code=400,
                details={'syntax_error': str(e)},
                suggestion='请提供有效的JSON数据'
            )
            return False, None, error_response

    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[tuple]) -> Optional[JsonResponse]:
        """
        验证必填字段

        Args:
            data: 请求数据
            required_fields: 必填字段列表，格式为 [(field_name, field_type, description), ...]

        Returns:
            错误响应或None
        """
        # 类型映射，避免使用eval
        type_map = {
            'str': str,
            'list': list,
            'int': int,
            'float': float,
            'bool': bool,
            'dict': dict
        }

        for field_name, field_type, description in required_fields:
            field_value = data.get(field_name)

            # 检查字段是否存在
            if field_value is None:
                return ErrorResponse.missing_field_error(
                    field_name=field_name,
                    expected_type=field_type,
                    suggestion=f'请提供{description}'
                )

            # 检查字段类型
            expected_type_class = type_map.get(field_type)
            if expected_type_class and not isinstance(field_value, expected_type_class):
                return ErrorResponse.validation_error(
                    message=f'{field_name}字段类型错误',
                    field_name=field_name,
                    expected_type=field_type,
                    received_type=type(field_value).__name__,
                    suggestion=f'{field_name}必须是{field_type}类型'
                )

            # 检查字符串是否为空
            if field_type == 'str' and not str(field_value).strip():
                return ErrorResponse.validation_error(
                    message=f'{field_name}字段不能为空',
                    field_name=field_name,
                    suggestion=f'请提供有效的{description}'
                )

        return None

    @staticmethod
    def validate_image_ids(image_ids: list) -> tuple[bool, List[str], Optional[JsonResponse]]:
        """验证图片ID列表"""
        if not isinstance(image_ids, list):
            error_response = ErrorResponse.validation_error(
                message='image_ids必须是列表格式',
                field_name='image_ids',
                expected_type='list',
                received_type=type(image_ids).__name__
            )
            return False, [], error_response

        valid_ids = []
        invalid_indices = []

        for i, image_id in enumerate(image_ids):
            if not isinstance(image_id, str) or not image_id.strip():
                invalid_indices.append(f"index_{i}")
            else:
                valid_ids.append(image_id.strip())

        if invalid_indices:
            error_response = ErrorResponse.create_error_response(
                error_code=ErrorCode.INVALID_FIELD_VALUE,
                error_message='image_ids包含无效的图片ID',
                status_code=400,
                details={
                    'invalid_indices': invalid_indices,
                    'expected_format': '每个ID必须是有效的字符串'
                },
                suggestion='请提供有效的图片ID列表'
            )
            return False, [], error_response

        return True, valid_ids, None

    @staticmethod
    def validate_numeric_parameters(data: Dict[str, Any]) -> Optional[JsonResponse]:
        """验证数值参数"""
        validation_errors = []

        # 验证max_tokens
        max_tokens = data.get('max_tokens')
        if max_tokens is not None:
            if not isinstance(max_tokens, int) or max_tokens <= 0:
                validation_errors.append({
                    'field': 'max_tokens',
                    'error': '必须是正整数',
                    'received_value': max_tokens
                })

        # 验证temperature
        temperature = data.get('temperature')
        if temperature is not None:
            if not isinstance(temperature, (int, float)) or not (0.0 <= temperature <= 2.0):
                validation_errors.append({
                    'field': 'temperature',
                    'error': '必须是0.0到2.0之间的数值',
                    'received_value': temperature
                })

        if validation_errors:
            return ErrorResponse.create_error_response(
                error_code=ErrorCode.VALIDATION_FAILED,
                error_message='参数验证失败',
                status_code=400,
                details={'validation_errors': validation_errors}
            )

        return None


def handle_service_exception(func_name: str, exception: Exception, context: Optional[Dict[str, Any]] = None) -> JsonResponse:
    """
    统一的服务异常处理器

    Args:
        func_name: 函数名
        exception: 异常对象
        context: 上下文信息

    Returns:
        错误响应
    """
    error_msg = str(exception)

    # 记录详细的错误日志
    log_message = f"{func_name}异常: {error_msg}"
    if context:
        log_message += f" - 上下文: {context}"

    logger.error(log_message, exc_info=True)

    # 根据错误类型返回相应的错误响应
    error_msg_lower = error_msg.lower()

    if any(keyword in error_msg_lower for keyword in ['invalidparameter', 'invalid parameter']):
        return ErrorResponse.ai_service_error(
            message='AI服务参数错误',
            details={'ai_error': error_msg},
            suggestion='请检查请求参数是否正确',
            original_error=error_msg
        )
    elif any(keyword in error_msg_lower for keyword in ['timeout', 'time out']):
        return ErrorResponse.ai_service_error(
            message='AI服务响应超时',
            details={'ai_error': error_msg},
            suggestion='请稍后重试',
            original_error=error_msg
        )
    elif any(keyword in error_msg_lower for keyword in ['rate limit', 'ratelimit', 'quota']):
        return ErrorResponse.ai_service_error(
            message='AI服务调用频率超限',
            details={'ai_error': error_msg},
            suggestion='请稍后重试或降低调用频率',
            original_error=error_msg
        )
    elif any(keyword in error_msg_lower for keyword in ['image_url', 'base64']):
        return ErrorResponse.image_upload_error(
            message='图片数据处理失败',
            details={'ai_error': error_msg},
            suggestion='请检查图片格式是否正确，或尝试重新上传图片'
        )
    else:
        return ErrorResponse.server_error(
            message='服务处理失败',
            original_error=error_msg
        )