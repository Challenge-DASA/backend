import time
import datetime
from typing import Optional

from quart import Blueprint, current_app, jsonify
from quart_schema import tag_blueprint, validate_response
from pydantic import BaseModel, Field

from application.middleware.context import get_context


class HealthResponse(BaseModel):
    status: str = Field(..., description="Application status")
    request_id: str = Field(..., description="Unique request identifier")
    timestamp: str = Field(..., description="Request timestamp")
    uptime: float = Field(..., description="Application uptime in seconds")


class VersionResponse(BaseModel):
    version: str = Field(..., description="Application version")
    api: str = Field(..., description="API name")
    build_date: Optional[str] = Field(None, description="Build date")
    git_commit: Optional[str] = Field(None, description="Git commit hash")
    environment: Optional[str] = Field(None, description="Runtime environment")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    request_id: Optional[str] = Field(None, description="Request identifier")
    timestamp: str = Field(..., description="Error timestamp")


system_bp = Blueprint('system', __name__)
tag_blueprint(system_bp, ["System"])

app_start_time = time.time()


@system_bp.get("/health")
@validate_response(ErrorResponse, 500)
async def health_check():
    try:
        context = get_context()
        current_time = time.time()
        uptime = current_time - app_start_time

        response_data = HealthResponse(
            status="healthy",
            request_id=str(context.request_id),
            timestamp=context.request_datetime.isoformat(),
            uptime=round(uptime, 2),
        )

        return jsonify(response_data.model_dump()), 200

    except (AttributeError, KeyError, ValueError, TypeError):
        try:
            context = get_context()
            request_id = context.request_id
        except (AttributeError, RuntimeError):
            request_id = None

        error_response = ErrorResponse(
            error="Health check failed",
            request_id=str(request_id) if request_id else None,
            timestamp=datetime.datetime.now(datetime.UTC).isoformat()
        )
        return jsonify(error_response.model_dump()), 500


@system_bp.get("/version")
@validate_response(ErrorResponse, 500)
async def version():
    try:
        response_data = VersionResponse(
            version=current_app.config.get('VERSION', '1.0.0'),
            api=current_app.config.get('API_NAME', 'SmartLab API'),
            build_date=current_app.config.get('BUILD_DATE'),
            git_commit=current_app.config.get('GIT_COMMIT'),
            environment=current_app.config.get('ENVIRONMENT', 'development')
        )

        return jsonify(response_data.model_dump()), 200

    except (AttributeError, KeyError):
        error_response = ErrorResponse(
            error="Unable to retrieve version information",
            request_id=None,
            timestamp=datetime.datetime.now(datetime.UTC).isoformat()
        )
        return jsonify(error_response.model_dump()), 500


@system_bp.errorhandler(Exception)
async def handle_exception(e):
    try:
        context = get_context()
        request_id = str(context.request_id)
    except (AttributeError, RuntimeError):
        request_id = None

    error_response = ErrorResponse(
        error="Internal server error",
        request_id=request_id,
        timestamp=datetime.datetime.now(datetime.UTC).isoformat()
    )
    return jsonify(error_response.model_dump()), 500