"""
Custom exception handler for consistent API error responses.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error response format.
    
    Response format:
    {
        "success": false,
        "error": {
            "code": "ERROR_CODE",
            "message": "Human readable message",
            "details": {} // optional additional details
        }
    }
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Log the error
        logger.error(f"API Error: {exc} | View: {context.get('view')} | Request: {context.get('request')}")
        
        # Customize the response format
        custom_response_data = {
            'success': False,
            'error': {
                'code': get_error_code(response.status_code),
                'message': get_error_message(response),
                'details': response.data if isinstance(response.data, dict) else {'error': response.data}
            }
        }
        
        response.data = custom_response_data
    
    return response


def get_error_code(status_code):
    """Map HTTP status codes to error codes."""
    error_codes = {
        400: 'BAD_REQUEST',
        401: 'UNAUTHORIZED',
        403: 'FORBIDDEN',
        404: 'NOT_FOUND',
        405: 'METHOD_NOT_ALLOWED',
        409: 'CONFLICT',
        422: 'UNPROCESSABLE_ENTITY',
        429: 'TOO_MANY_REQUESTS',
        500: 'INTERNAL_SERVER_ERROR',
    }
    return error_codes.get(status_code, 'UNKNOWN_ERROR')


def get_error_message(response):
    """Extract a human-readable error message from the response."""
    if isinstance(response.data, dict):
        # Check for common error message fields
        for field in ['detail', 'message', 'error', 'non_field_errors']:
            if field in response.data:
                value = response.data[field]
                if isinstance(value, list):
                    return value[0] if value else 'An error occurred'
                return str(value)
        
        # If no common field found, return first error
        for key, value in response.data.items():
            if isinstance(value, list) and value:
                return f"{key}: {value[0]}"
            elif value:
                return f"{key}: {value}"
    
    return str(response.data) if response.data else 'An error occurred'
