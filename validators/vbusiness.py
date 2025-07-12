from bson import Regex
from fastapi import Request


async def validate_business_name(name: str, request: Request) -> str:
    """
    Validate business name

    :param name: The business name to validate.
    :param request: FastAPI request object.
    :return: A message if a business with the same name exists, otherwise None.
    """
    # MongoDB: businesses collection/table
    businesses_table = request.app.state.mongo_database["businesses"]

    # Ensure: name contains no whitespaces and is lowercase
    name: str = "".join(name.split()).lower()

    # MongoDB: find business with name
    business = await businesses_table.find_one({"admin_id": request.app.state.admin_id, "name_lower": name})

    if isinstance(business, dict):
        return f"business with same name exists"