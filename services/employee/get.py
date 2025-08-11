from fastapi import Request
from core.formatters import iso_format_datetime
from typing import Any
from bson import ObjectId, errors as bson_error


async def get_employee(request: Request, employee_id: str) -> None | dict[str, Any]:
    """
    Retrieve employee data.

    :param request: Request object.
    :param employee_id: String ObjectId of employee.
    :return: A dictionary with employee data.
    :raises ValueError: If employee_id is invalid or employee with matching ObjectId does not exist.
    """

    # MONGODB: assign admins collection/table
    admins_table = request.app.state.mongo_database["employees"]

    try:
        query = {
            '_id': ObjectId(employee_id),
        }
    except bson_error.InvalidId:
        raise ValueError("invalid employee_id")
    
    # MONGODB: find employee with matching id
    employee_db_data = await admins_table.find_one(query)

    # ENSURE: employee is a dictionary
    if isinstance(employee_db_data, dict):

        # Remove password from the admin data
        employee_db_data.pop("password")

        # Serialize ObjectId to string for JSON compatibility
        employee_db_data["_id"] = str(employee_db_data["_id"])
        employee_db_data["admin_id"] = str(request.app.state.admin_id)
        employee_db_data["business_id"] = str(request.app.state.business_id)

        # ISO format datetime
        employee_db_data["created_at"] = iso_format_datetime(employee_db_data["created_at"])

        return employee_db_data
    else:
        raise ValueError("invalid employee_id")


async def get_employees(request: Request, business_id: str) -> None | list[dict[str, Any]]:
    """
    Retrieve all employees data of a specific business.

    :param request: Request object.
    :param business_id: String ObjectId of target business.
    :return: A list with employees data or None if no employees exist.
    """
    # MONGODB: assign employees collection/table
    employees_table = request.app.state.mongo_database["employees"]

    # MONGODB: projection to return only necessary fields.
    # fields not mentioned here will not be returned and
    # _id is included by default
    projection = {
        'name': True,
        'username': True,
        'email': True,
        'business_id': True,
        'is_active': True,
        'created_at': True
    }

    try:
        query = {
            'admin_id': request.app.state.admin_id,
            'business_id': ObjectId(business_id),
        }
    except bson_error.InvalidId:
        raise ValueError("invalid business_id")

    # MONGODB: find employees with matching admin_id & business_id
    employees_db_data = await employees_table.find(query, projection).to_list(length=None)

    # List of all retrieved employees
    result_employees = []
    for employee in employees_db_data:
        if isinstance(employee, dict):

            # Serialize ObjectId to string for JSON compatibility
            employee["_id"] = str(employee["_id"])
            employee["business_id"] = str(employee["business_id"])

            # ISO format datetime
            employee["created_at"] = iso_format_datetime(employee["created_at"])

            # Append employee into result employees
            result_employees.append(employee)

    # ENSURE: at least one employee exists
    if len(result_employees) == 0:
        return None

    return result_employees