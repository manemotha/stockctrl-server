from fastapi import Request
from core.formatters import iso_format_datetime
from typing import Any
from bson import ObjectId

async def get_employee(request: Request, employee_id: ObjectId) -> None | dict[str, Any]:
    """
    Retrieve employee data.

    :param request: Request object.
    :param employee_id: Employee ObjectId.
    :return: A dictionary with employee data.
    :raises ValueError: If employee does not exist.
    """

    # MONGODB: assign admins collection/table
    admins_table = request.app.state.mongo_database["employees"]

    # MONGODB: find employee with matching id
    employee_db_data = await admins_table.find_one(
        {"_id": employee_id},
    )

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
        raise ValueError("employee does not exist")