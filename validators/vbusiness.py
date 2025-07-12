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

    # MongoDB: find business with name
    business = await businesses_table.find_one({"admin_id": request.app.state.admin_id, "name": name.lower()})

    if isinstance(business, dict):
        return f"business with same name exists"