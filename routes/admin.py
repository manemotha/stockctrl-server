import pymongo.errors
from fastapi import APIRouter, Request, status

from models.admin import *
from services.auth import validate_username, validate_password, hash_password
from utils.controllers import http_response

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