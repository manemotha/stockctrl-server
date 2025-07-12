from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from services.auth import *
from validators.vcredentials import *
from validators.vadmin import validate_admin_token
from datetime import datetime, timezone
from utils.controllers import http_response
from models.admin import *
import pymongo.errors
from typing import Any

admin_routes = APIRouter()


@admin_routes.post("/")
async def create_admin(payload: AdminSignupModel, request: Request):

    # Read the payload and convert it to a dictionary
    admin_data: dict[str, Any] = payload.model_dump()

    # MongoDB: Declare admins collection/table
    admins_table = request.app.state.mongo_database["admins"]

    # Validate: username
    username_validation_result = validate_username(admin_data["username"])
    if username_validation_result != "valid username":
        return http_response(message=username_validation_result, status_code=status.HTTP_400_BAD_REQUEST)

    try:
        # MongoDB: find admin with matching username
        admin_exists_result = await admins_table.find_one({"username": admin_data["username"]})
    except pymongo.errors.ServerSelectionTimeoutError:
        return http_response(message="error connecting to mongodb server", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Response for when admin with username exists
    if admin_exists_result:
        return http_response(message="account with username exists", status_code=status.HTTP_409_CONFLICT)

    # Validate: password
    user_password = admin_data["password"]
    password_validation_result = validate_password(user_password)

    if password_validation_result == "valid password":
        # Generate hashed admin password
        hashed_password: bytes = hash_password(user_password)

        # Attach hashed password to admin_data
        admin_data["password"] = hashed_password

        # MongoDB: insert admin_data
        await admins_table.insert_one(admin_data)
        return http_response(message="admin account created", status_code=status.HTTP_201_CREATED)
    else:
        return http_response(message=password_validation_result, status_code=status.HTTP_400_BAD_REQUEST)


@admin_routes.get("/token")
@validate_admin_token()
async def auth_token(request: Request):
    return http_response(message="valid auth_token", status_code=status.HTTP_200_OK)


@admin_routes.post("/token")
async def create_admin_auth_token(payload: AdminSigninModel, request: Request):

    # Read the payload and convert it to a dictionary
    admin_data: dict[str, Any] = payload.model_dump()

    # MongoDB: Declare admins collection/table
    admins_table = request.app.state.mongo_database["admins"]

    # MongoDB: find admin with matching username
    admin_db_data = await admins_table.find_one({"username": admin_data["username"]})

    # Ensure: username & password verification process takes consistent response time
    verification_result = await verify_login_credentials(admin_data, admin_db_data)
    if verification_result == "invalid credentials":
        return http_response(message=verification_result, status_code=status.HTTP_401_UNAUTHORIZED)

    # Assign: token and expires_at
    token, expires_at = verification_result["token"], verification_result["expires_at"]

    # Declare session_token data
    session_token_data = {
        "token": token,
        "admin_id": admin_db_data["_id"],
        "created_at": datetime.now(timezone.utc),
        "expires_at": expires_at,
        "is_replaced": False,
        "replaced_at" : None,
        "replaced_by": None,
        "revoked": False,
        "revoked_at": None,
        "is_admin": True
    }

    # MongoDB: Declare session_tokens collection/table
    session_tokens_table = request.app.state.mongo_database["session_tokens"]

    # MongoDB: insert session_token into session_tokens collection/table
    await session_tokens_table.insert_one(session_token_data)

    # Return success response with session token
    return JSONResponse(content={"message": "admin auth_token created", "token": token, "is_admin": True}, status_code=status.HTTP_201_CREATED)


@admin_routes.delete("/token")
@validate_admin_token()
async def revoke_admin_auth_token(request: Request):

    # Revoke the auth token
    await revoke_auth_token(request=request, token=request.app.state.token)

    # Remove admin_id and token from the app state
    request.app.state.admin_id = None
    request.app.state.token = None

    return http_response(message="revoked auth_token", status_code=status.HTTP_200_OK)