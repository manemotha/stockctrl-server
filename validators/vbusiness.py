from fastapi import Request
from bson import ObjectId, errors as bson_error


async def check_business_exists(business_id: str, request: Request) -> None:
    """
    Check business existence without returning data.

    :param business_id: The business ID to validate.
    :param request: FastAPI request object.
    :raise ValueError: If the business_id is invalid or does not exist.
    """
    try:
        query = {
            '_id': ObjectId(business_id),
            'admin_id': request.app.state.admin_id
        }
    except bson_error.InvalidId:
        raise ValueError("invalid business_id")

    # MONGODB: businesses collection/table
    businesses_table = request.app.state.mongo_database["businesses"]

    # ENSURE: business exists
    if await businesses_table.find_one(query, limit=1) is None:
        raise ValueError("invalid business_id")


async def validate_business_name(name: str, request: Request) -> str:
    """
    Validate business name

    :param name: The business name to validate.
    :param request: FastAPI request object.
    :return: A message if a business with the same name exists, otherwise None.
    """
    # MONGODB: businesses collection/table
    businesses_table = request.app.state.mongo_database["businesses"]

    # ENSURE: name contains no whitespaces and is lowercase
    name: str = "".join(name.split()).lower()

    # MONGODB: find business with name
    business = await businesses_table.find_one({"admin_id": request.app.state.admin_id, "name_lower": name})

    if isinstance(business, dict):
        return f"business with same name exists"