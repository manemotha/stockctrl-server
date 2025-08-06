from fastapi import Request, status
from functools import wraps
from core.http_responses import http_response
from datetime import datetime, timezone


def validate_employee_token():
    """
    Decorator to validate authentication token from the request header.

    Used to protect routes that require authentication.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):

            # MONGODB: assign session_tokens collection/table
            session_tokens_table = request.app.state.mongo_database["session_tokens"]

            # Get auth_token from authorization header
            auth_header = request.headers.get("authorization")
            if not auth_header:
                return http_response(message="missing authorization header", status_code=status.HTTP_401_UNAUTHORIZED)

            # VALIDATE: auth_token is in correct format
            token = auth_header.replace("Bearer", "").strip()

            # MONGODB: find user with matching session_token
            employee_db_data = await session_tokens_table.find_one({"is_admin": False, "token": token})

            # VALIDATE: token is invalid
            if not employee_db_data or not isinstance(employee_db_data, dict):
                return http_response(message="invalid employee auth_token", status_code=status.HTTP_401_UNAUTHORIZED)

            # VALIDATE: token is revoked
            if employee_db_data["revoked"] and employee_db_data["revoked_at"]:
                return http_response(message="revoked employee auth_token", status_code=status.HTTP_401_UNAUTHORIZED)

            # Assign auth_token expiration date
            expires_at = employee_db_data["expires_at"]

            # VALIDATE: token is expired
            if expires_at < datetime.now(timezone.utc):
                return http_response(message="expired employee auth_token", status_code=status.HTTP_401_UNAUTHORIZED)

            # Store admin_id, employee_id, business_id and token in the app state
            request.app.state.admin_id = employee_db_data["admin_id"]
            request.app.state.employee_id = employee_db_data["employee_id"]
            request.app.state.business_id = employee_db_data["business_id"]
            request.app.state.token = employee_db_data["token"]
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator