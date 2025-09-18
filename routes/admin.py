from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from services.auth import *
from services.business.get import get_business, get_businesses
from services.business.delete import delete_business
from services.admin.get import get_admin
from services.employee.get import get_employees, get_employee
from validators.vcredentials import *
from validators.vadmin import validate_admin_token
from validators.vbusiness import validate_business_name
from datetime import datetime, timezone
from core.http_responses import http_response
from models.admin import *
from models.business import *
import pymongo.errors
from typing import Any

admin_routes = APIRouter()


@admin_routes.post("/")
async def create_admin(payload: AdminSignupModel, request: Request):

    # Read the payload and convert it to a dictionary
    admin_data: dict[str, Any] = payload.model_dump()

    # MONGODB: Declare admins collection/table
    admins_table = request.app.state.mongo_database["admins"]

    # VALIDATE: username
    username_validation_result = validate_username(admin_data["username"])
    if username_validation_result != "valid username":
        return http_response(message=username_validation_result, status_code=status.HTTP_400_BAD_REQUEST)

    try:
        # MONGODB: find admin with matching username
        admin_exists_result = await admins_table.find_one({"username": admin_data["username"]})
    except pymongo.errors.ServerSelectionTimeoutError:
        return http_response(message="error connecting to mongodb server", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Response for when admin with username exists
    if admin_exists_result:
        return http_response(message="account with username exists", status_code=status.HTTP_409_CONFLICT)

    # VALIDATE: password
    user_password = admin_data["password"]
    password_validation_result = validate_password(user_password)

    if password_validation_result == "valid password":
        # Generate hashed admin password
        hashed_password: bytes = hash_password(user_password)

        # Attach hashed password to admin_data
        admin_data["password"] = hashed_password

        # MONGODB: insert admin_data
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

    # MONGODB: Declare admins collection/table
    admins_table = request.app.state.mongo_database["admins"]

    # MONGODB: find admin with matching username
    admin_db_data = await admins_table.find_one({"username": admin_data["username"]})

    # ENSURE: username & password verification process takes consistent response time
    verification_result = await verify_login_credentials(admin_data, admin_db_data)
    if verification_result == "invalid credentials":
        return http_response(message=verification_result, status_code=status.HTTP_401_UNAUTHORIZED)

    # Assign token and expires_at
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

    # MONGODB: Declare session_tokens collection/table
    session_tokens_table = request.app.state.mongo_database["session_tokens"]

    # MONGODB: insert session_token into session_tokens collection/table
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

    return http_response(message="revoked admin auth_token", status_code=status.HTTP_200_OK)


@admin_routes.get("/")
@validate_admin_token()
async def get_admin_profile(request: Request):

    try:
        # Get admin profile data
        admin_profile = await get_admin(request)

        return JSONResponse(
            content={
                "message": "admin found",
                "data": admin_profile
            }, status_code=status.HTTP_200_OK)
    except ValueError:
        return http_response(message="admin not found", status_code=status.HTTP_404_NOT_FOUND)


@admin_routes.post("/business")
@validate_admin_token()
async def create_new_business(request: Request, payload: CreateBusinessModel):

    # Read the payload and convert it to a dictionary
    business_data: dict[str, Any] = payload.model_dump()

    # ENSURE: business type is service-based
    if business_data["type"] == BusinessType.PRODUCT.value:
        return http_response(message=f"{BusinessType.PRODUCT.value} logic is not yet supported, use {BusinessType.SERVICE.value} instead.", status_code=status.HTTP_501_NOT_IMPLEMENTED)

    # Assign business name
    business_name = business_data["name"]

    # VALIDATE: business name
    validation_result = await validate_business_name(business_name, request)
    if validation_result:
        return http_response(message=validation_result, status_code=status.HTTP_409_CONFLICT)

    # ENSURE: business name contains no whitespaces and is lowercase
    # Key name_lower is used to query MongoDB
    name_lower: str = "".join(business_name.split()).lower()

    # Insert system additional fields
    business_data['name_lower'] = name_lower
    business_data['admin_id'] = request.app.state.admin_id
    business_data['created_at'] = datetime.now(timezone.utc)
    business_data['is_active'] = True

    # MONGODB: assign businesses collection/table
    businesses_table = request.app.state.mongo_database["businesses"]

    # MONGODB: insert new business data
    new_business = await businesses_table.insert_one(business_data)

    # ObjectId of the newly inserted business
    business_id = str(new_business.inserted_id)

    return JSONResponse(content={"message": "business created", "business_id": business_id}, status_code=status.HTTP_201_CREATED)


@admin_routes.delete("/business/{business_id}")
@validate_admin_token()
async def remove_business_by_id(request: Request, business_id: str):

    try:
        # Delete business with matching business_id
        await delete_business(request, business_id)
        return http_response(message="business removed", status_code=status.HTTP_200_OK)
    except ValueError:
        return http_response(message="invalid business_id", status_code=status.HTTP_404_NOT_FOUND)


@admin_routes.get("/business/{business_id}")
@validate_admin_token()
async def get_business_by_id(request: Request, business_id: str):

    try:
        # Get business with matching business_id
        business_db_data = await get_business(request, business_id)

        return JSONResponse(
            content={
                "message": "business found",
                "data": business_db_data,
            }, status_code=status.HTTP_200_OK)
    except ValueError:
        return http_response(message="invalid business_id", status_code=status.HTTP_404_NOT_FOUND)


@admin_routes.get("/businesses")
@validate_admin_token()
async def get_all_businesses(request: Request):

    try:
        #
        businesses_found = await get_businesses(request)
    except ValueError:
        return http_response(message="no businesses found", status_code=status.HTTP_404_NOT_FOUND)

    # ENSURE: businesses_found is a list
    if businesses_found is None:
        return http_response(message="no businesses found", status_code=status.HTTP_404_NOT_FOUND)

    return JSONResponse(content={"message": "businesses found", "data": businesses_found}, status_code=status.HTTP_200_OK)


@admin_routes.get("/employee/{business_id}/{employee_id}")
@validate_admin_token()
async def get_employee_by_id(request: Request, business_id: str, employee_id: str):

    try:
        # Get employee with matching employee_id
        employee_db_data = await get_employee(request, business_id, employee_id)

        return JSONResponse(
            content={
                "message": "employee found",
                "data": employee_db_data,
            }, status_code=status.HTTP_200_OK)

    except ValueError as error:

        # Convert error to string for comparison
        error = str(error)

        if error == "invalid business_id":
            return http_response(message="invalid business_id", status_code=status.HTTP_404_NOT_FOUND)

        return http_response(message="invalid employee_id", status_code=status.HTTP_404_NOT_FOUND)


@admin_routes.get("/employees/{business_id}")
@validate_admin_token()
async def get_all_employees(request: Request, business_id: str):

    try:
        employees_found = await get_employees(request, business_id)
    except ValueError as error:

        if str(error) == "invalid business_id":
            return http_response(message="invalid business_id", status_code=status.HTTP_404_NOT_FOUND)

        return http_response(message="no employees found", status_code=status.HTTP_404_NOT_FOUND)

    # ENSURE: employees_found is a list
    if employees_found is None:
        return http_response(message="no employees found", status_code=status.HTTP_404_NOT_FOUND)

    return JSONResponse(content={"message": "employees found", "data": employees_found}, status_code=status.HTTP_200_OK)


@admin_routes.delete("/employee/tokens/{employee_id}")
@validate_admin_token()
async def revoke_all_employee_tokens(request: Request, employee_id: str):

    try:
        # Revoke all active employee tokens
        await revoke_employee_auth_tokens(request=request, employee_id=employee_id)
    except ValueError as error:

        # Handle invalid employee_id error
        if error == "invalid employee_id":
            return http_response(message=str(error), status_code=status.HTTP_404_NOT_FOUND)

        return http_response(message="employee has no active auth_tokens", status_code=status.HTTP_404_NOT_FOUND)

    return http_response(message=f"revoked all employee auth_tokens", status_code=status.HTTP_200_OK)