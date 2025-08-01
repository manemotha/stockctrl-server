from fastapi import Request
from typing import Any

async def get_admin(request: Request) -> None | dict[str, Any]:
    """
    Retrieve admin data.

    :param request: Request object.
    :return: A dictionary with admin data.
    :raises ValueError: If admin does not exist.
    """

    # MONGODB: assign admins collection/table
    admins_table = request.app.state.mongo_database["admins"]

    # MONGODB: find admin with matching id
    admin_db_data = await admins_table.find_one(
        {"_id": request.app.state.admin_id}
    )

    # ENSURE: admin is a dictionary
    if isinstance(admin_db_data, dict):

        # Remove password from the admin data
        admin_db_data.pop("password")

        # Serialize ObjectId to string for JSON compatibility
        admin_db_data["_id"] = str(admin_db_data["_id"])

        return admin_db_data
    else:
        raise ValueError("admin does not exist")