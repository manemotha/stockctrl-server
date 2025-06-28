from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from services.auth import *
from datetime import datetime, timezone
from utils.controllers import http_response
from models.admin import *
import asyncio
import pymongo.errors

admin_routes = APIRouter()


@admin_routes.post("/create")
async def create_admin(payload: AdminSignupModel, request: Request):

    # Read the payload and convert it to a dictionary
    admin_data: dict = payload.model_dump()

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
        return http_response(message="account with username exists", status_code=400)

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
        return http_response(message="admin account created", status_code=200)
    else:
        return http_response(message=password_validation_result, status_code=400)


@admin_routes.post("/auth_token")
async def create_admin_auth_token(payload: AdminSigninModel, request: Request):

    # Read the payload and convert it to a dictionary
    admin_data: dict = payload.model_dump()

    # MongoDB: Declare admins collection/table
    admins_table = request.app.state.mongo_database["admins"]

    # MongoDB: find admin with matching username
    admin_db_data = await admins_table.find_one({"username": admin_data["username"]})

    # Validate: admin username and password
    if not admin_db_data or not isinstance(admin_db_data, dict) or not compare_hashed_password(admin_data["password"], admin_db_data["password"]):
        await asyncio.sleep(1.5) # delay response by 1.5 seconds
        return http_response(message="invalid credentials", status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        # Generate auth_token
        token = generate_auth_token()["token"]
        expires_at = generate_auth_token()["expires_at"]
    except KeyError:
        return http_response(message="error generating auth_token", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Declare session_token data
    session_token_data = {
        "token": token,
        "admin_id": admin_db_data["_id"],
        "created_at": datetime.now(timezone.utc),
        "expires_at": expires_at,
        "revoked": False,
        "revoked_at": None,
        "is_admin": True
    }

    # MongoDB: Declare session_tokens collection/table
    session_tokens_table = request.app.state.mongo_database["session_tokens"]

    # MongoDB: insert session_token into session_tokens collection/table
    await session_tokens_table.insert_one(session_token_data)

    # Return success response with session token
    return JSONResponse(content={"message": "admin auth_token created", "token": token, "is_admin": True}, status_code=status.HTTP_200_OK)