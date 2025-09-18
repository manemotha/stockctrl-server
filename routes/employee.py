from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from models.employee import EmployeeSigninModel, EmployeeSignupModel
from services.auth import *
from services.business.get import get_business
from services.employee.get import get_employee
from validators.vadmin import validate_admin_token
from validators.vcredentials import validate_username, validate_password
from validators.vemployee import validate_employee_token
from datetime import datetime, timezone
from core.http_responses import http_response
from typing import Any
from bson import ObjectId, errors as bson_error

employee_routes = APIRouter()


@employee_routes.post("/")
@validate_admin_token()
async def add_new_employee(request: Request, payload: EmployeeSignupModel):

    # Read the payload and convert it to a dictionary
    employee_data: dict[str, Any] = payload.model_dump()

    # VALIDATE: username
    username_validation_result = validate_username(employee_data['username'])
    if username_validation_result != "valid username":
        return http_response(message=username_validation_result, status_code=status.HTTP_400_BAD_REQUEST)

    # MONGODB: assign employees collection/table
    employees_table = request.app.state.mongo_database["employees"]

    # Check if employee with username exists
    query = {
        "admin_id": request.app.state.admin_id,
        "username": employee_data["username"]
    }
    if await employees_table.find_one(query):
        return http_response(message="employee with username exists", status_code=status.HTTP_409_CONFLICT)

    try:
        query = {
            '_id': ObjectId(employee_data['business_id']),
            'admin_id': request.app.state.admin_id
        }
    except bson_error.InvalidId:
        # ObjectId can not be initialized from business_id
        return http_response(message="invalid business_id", status_code=status.HTTP_400_BAD_REQUEST)

    # MONGODB: assign businesses collection/table
    businesses_table = request.app.state.mongo_database["businesses"]

    # Find business with matching admin_id & business_id
    business_db_data = await businesses_table.find_one(query)

    # VALIDATE: business
    if not business_db_data or not isinstance(business_db_data, dict):
        return http_response(message="invalid business_id", status_code=status.HTTP_400_BAD_REQUEST)

    # Insert system additional fields
    employee_data['business_id'] = business_db_data['_id']
    employee_data['admin_id'] = request.app.state.admin_id
    employee_data['created_at'] = datetime.now(timezone.utc)
    employee_data['is_active'] = True
    employee_data['is_admin'] = False

    # VALIDATE: password
    employee_password = employee_data['password']
    password_validation_result = validate_password(employee_password)

    if password_validation_result != "valid password":
        return http_response(message=password_validation_result, status_code=status.HTTP_400_BAD_REQUEST)

    # Hash employee password
    hashed_password: bytes = hash_password(employee_password)

    # Insert hashed password into employee_data
    employee_data["password"] = hashed_password

    # MONGODB: insert new employee data
    new_employee = await employees_table.insert_one(employee_data)

    return JSONResponse(
        content={
            "message": "employee added",
            "employee_id": str(new_employee.inserted_id)
        },
        status_code=status.HTTP_201_CREATED
    )


@employee_routes.post("/token")
@validate_admin_token()
async def create_employee_auth_token(request: Request, payload: EmployeeSigninModel):

    # Read the payload and convert it to a dictionary
    employee_data: dict[str, Any] = payload.model_dump()

    # MONGODB: assign employees collection/table
    employees_table = request.app.state.mongo_database["employees"]

    # MONGODB: get employee data from database
    employee_db_data = await employees_table.find_one({"admin_id": request.app.state.admin_id, "username": employee_data["username"]})

    # ENSURE: username & password verification process takes consistent response time
    verification_result = await verify_login_credentials(employee_data, employee_db_data)
    if verification_result == "invalid credentials":
        return http_response(message=verification_result, status_code=status.HTTP_401_UNAUTHORIZED)

    # Assign token and expires_at
    token, expires_at = verification_result["token"], verification_result["expires_at"]

    # Complete employee token data
    session_token_data = {
        "token": token,
        "employee_id": employee_db_data["_id"],
        "admin_id": employee_db_data["admin_id"],
        "business_id": employee_db_data["business_id"],
        "created_at": datetime.now(timezone.utc),
        "expires_at": expires_at,
        "revoked": False,
        "revoked_at": None,
        "is_admin": False
    }

    # Replace admin token with employee token
    await replace_admin_auth_token(request, session_token_data["employee_id"])

    # MONGODB: assign session_tokens collection/table
    session_tokens_table = request.app.state.mongo_database["session_tokens"]

    # MONGODB: insert token into session_tokens collection/table
    await session_tokens_table.insert_one(session_token_data)

    return JSONResponse(content={"message": "employee auth_token created", "token": token, "is_admin": False}, status_code=status.HTTP_201_CREATED)


@employee_routes.delete("/token")
@validate_employee_token()
async def revoke_employee_auth_token(request: Request):

    # Revoke the auth token
    await revoke_auth_token(request=request, token=request.app.state.token)

    # Remove admin_id, employee_id and token from the app state
    request.app.state.admin_id = None
    request.app.state.employee_id = None
    request.app.state.token = None

    return http_response(message="revoked employee auth_token", status_code=status.HTTP_200_OK)


@employee_routes.get("/token")
@validate_employee_token()
async def validate_employee_auth_token(request: Request):
    return http_response(message="valid employee auth_token", status_code=status.HTTP_200_OK)


@employee_routes.get("/business")
@validate_employee_token()
async def get_business_by_id(request: Request):

    # NOTE: employee get_business_by_id route does not require business_id
    # because it is already stored in the app state after employee login.
    # We can directly use request.app.state.business_id.

    try:
        # Get business with matching business_id
        business_db_data = await get_business(request, request.app.state.business_id)

        return JSONResponse(
            content={
                "message": "business found",
                "data": business_db_data,
            }, status_code=status.HTTP_200_OK)
    except ValueError:
        return http_response(message="invalid business_id", status_code=status.HTTP_404_NOT_FOUND)


@employee_routes.get("/")
@validate_employee_token()
async def get_employee_by_id(request: Request):

    # NOTE: employee get_employee_by_id route does not require employee_id
    # because it is already stored in the app state after employee login.
    # We can directly use request.app.state.employee_id.

    try:
        # Get employee with matching employee_id
        employee_db_data = await get_employee(request, str(request.app.state.business_id), str(request.app.state.employee_id))

        return JSONResponse(
            content={
                "message": "employee found",
                "data": employee_db_data,
            }, status_code=status.HTTP_200_OK)
    except ValueError:
        return http_response(message="invalid employee_id", status_code=status.HTTP_404_NOT_FOUND)