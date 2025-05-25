import datetime
import uuid
from typing import Dict, Any, Optional, Tuple

from quart import Quart, jsonify
from pydantic import BaseModel, Field

from application.exceptions import ApplicationError
from application.middleware.context import get_context
from domain.value_objects.ids import InvalidResourceIdError


class ErrorDetail(BaseModel):
    type: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional error details")


class ErrorContext(BaseModel):
    request_id: Optional[uuid.UUID] = Field(None, description="Request identifier")
    timestamp: str = Field(..., description="Error timestamp")


class ErrorResponse(BaseModel):
    error: ErrorDetail = Field(..., description="Error information")
    context: ErrorContext = Field(..., description="Error context")


def _get_safe_context() -> ErrorContext:
    try:
        context = get_context()
        return ErrorContext(
            request_id=context.request_id,
            timestamp=context.request_datetime.isoformat()
        )
    except (AttributeError, RuntimeError):
        return ErrorContext(
            request_id=None,
            timestamp=datetime.datetime.now(datetime.UTC).isoformat()
        )


def _build_error_response(
        error_type: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
) -> Tuple[Dict[str, Any], ErrorContext]:
    context = _get_safe_context()

    error_response = ErrorResponse(
        error=ErrorDetail(
            type=error_type,
            message=message,
            details=details or {}
        ),
        context=context
    )

    return error_response.model_dump(), context


def register_error_handlers(app: Quart) -> None:
    @app.errorhandler(ApplicationError)
    async def handle_application_error(error: ApplicationError):
        response_data, context = _build_error_response(
            error_type=error.__class__.__name__,
            message=error.message,
            details=error.details
        )
        return jsonify(response_data), 400

    @app.errorhandler(InvalidResourceIdError)
    async def handle_invalid_resource_id_error(error: InvalidResourceIdError):
        response_data, context = _build_error_response(
            error_type="InvalidResourceIdError",
            message="Invalid resource ID",
            details={
                "field": error.field,
                "invalid_value": error.invalid_value
            }
        )
        return jsonify(response_data), 400

    @app.errorhandler(ValueError)
    async def handle_value_error(error: ValueError):
        response_data, context = _build_error_response(
            error_type="ValidationError",
            message=str(error)
        )
        return jsonify(response_data), 400

    @app.errorhandler(KeyError)
    async def handle_key_error(error: KeyError):
        response_data, context = _build_error_response(
            error_type="MissingFieldError",
            message=f"Required field missing: {str(error)}",
            details={"missing_field": str(error).strip("'")}
        )
        return jsonify(response_data), 400

    @app.errorhandler(404)
    async def handle_not_found(error):
        response_data, context = _build_error_response(
            error_type="NotFoundError",
            message="Resource not found"
        )
        return jsonify(response_data), 404

    @app.errorhandler(405)
    async def handle_method_not_allowed(error):
        response_data, context = _build_error_response(
            error_type="MethodNotAllowedError",
            message="Method not allowed"
        )
        return jsonify(response_data), 405

    @app.errorhandler(422)
    async def handle_unprocessable_entity(error):
        response_data, context = _build_error_response(
            error_type="ValidationError",
            message="Request validation failed",
            details=getattr(error, 'description', {}) if hasattr(error, 'description') else {}
        )
        return jsonify(response_data), 422

    @app.errorhandler(Exception)
    async def handle_generic_error(error: Exception):
        context = _get_safe_context()

        app.logger.error(
            f"Unhandled error: {str(error)} | Request ID: {context.request_id}",
            exc_info=True
        )

        response_data, _ = _build_error_response(
            error_type="InternalServerError",
            message="An internal error occurred"
        )
        return jsonify(response_data), 500