from fastapi import APIRouter, status
from models.employee import AddEmployeeModel
from services.auth import *
from validators.vauthtoken import validate_admin_token
from validators.vcredentials import validate_username, validate_password
from datetime import datetime, timezone
from utils.controllers import http_response
from typing import Any
from bson import ObjectId, errors as bson_error

employee_routes = APIRouter()


@employee_routes.post("/")
@validate_admin_token()
async def add_new_employee(request: Request, payload: AddEmployeeModel):

    # Read the payload and convert it to a dictionary
    employee_data: dict[str, Any] = payload.model_dump()

    # Validate: username
    username_validation_result = validate_username(employee_data['username'])
    if username_validation_result != "valid username":
        return http_response(message=username_validation_result, status_code=status.HTTP_400_BAD_REQUEST)

    # MongoDB: assign employees collection/table
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

    # MongoDB: assign businesses collection/table
    businesses_table = request.app.state.mongo_database["businesses"]

    # Find business with matching admin_id & business_id
    business_db_data = await businesses_table.find_one(query)

    # Validate: business
    if not business_db_data or not isinstance(business_db_data, dict):
        return http_response(message="invalid business_id", status_code=status.HTTP_400_BAD_REQUEST)

    # Insert system additional fields
    employee_data['business_id'] = business_db_data['_id']
    employee_data['admin_id'] = request.app.state.admin_id
    employee_data['created_at'] = datetime.now(timezone.utc)
    employee_data['is_active'] = True
    employee_data['is_admin'] = False

    # Validate: password
    employee_password = employee_data['password']
    password_validation_result = validate_password(employee_password)

    if password_validation_result != "valid password":
        return http_response(message=password_validation_result, status_code=status.HTTP_400_BAD_REQUEST)

    # Hash employee password
    hashed_password: bytes = hash_password(employee_password)

    # Insert hashed password into employee_data
    employee_data["password"] = hashed_password

    # MongoDB: insert new employee data
    await employees_table.insert_one(employee_data)

    return http_response(message="employee created", status_code=status.HTTP_201_CREATED)