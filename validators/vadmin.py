from fastapi import Request, status
from functools import wraps
from utils.controllers import http_response
from datetime import datetime, timezone


def validate_admin_token():
    """
    Decorator to validate authentication token from the request header.

    Used to protect routes that require authentication.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):

            # MONGODB: Declare auth_tokens collection/table
            auth_tokens_table = request.app.state.mongo_database["session_tokens"]

            # Get auth_token from authorization header
            auth_header = request.headers.get("authorization")
            if not auth_header:
                return http_response(message="missing authorization header", status_code=status.HTTP_401_UNAUTHORIZED)

            # VALIDATE: auth_token is in correct format
            token = auth_header.replace("Bearer", "").strip()

            # MONGODB: find user with matching session_token
            user_db_data = await auth_tokens_table.find_one({"is_admin": True, "token": token})

            # VALIDATE: token is invalid
            if not user_db_data or not isinstance(user_db_data, dict):
                return http_response(message="invalid admin auth_token", status_code=status.HTTP_401_UNAUTHORIZED)

            # VALIDATE: token is revoked
            if user_db_data["revoked"] and user_db_data["revoked_at"]:
                return http_response(message="revoked admin auth_token", status_code=status.HTTP_401_UNAUTHORIZED)

            # VALIDATE: token is replaced
            if user_db_data["is_replaced"] and user_db_data["replaced_at"] and user_db_data["replaced_by"]:
                return http_response(message="replaced admin auth_token", status_code=status.HTTP_401_UNAUTHORIZED)

            # Assign auth_token expiration date
            expires_at = user_db_data["expires_at"]

            # VALIDATE: token is expired
            if expires_at < datetime.now(timezone.utc):
                return http_response(message="expired auth_token", status_code=status.HTTP_401_UNAUTHORIZED)

            # Store admin_id and token in the app state
            request.app.state.admin_id = user_db_data["admin_id"]
            request.app.state.token = user_db_data["token"]
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator