from fastapi import Request


async def validate_business_name(name: str, request: Request) -> str:
    """
    Validate business name

    **Args:**
     name (str)\n
     request (FastAPI Request)

    **Return:**
     String (str)
    """
    # MongoDB: businesses collection/table
    businesses_table = request.app.state.mongo_database["businesses"]

    # MongoDB: find business with name
    business = await businesses_table.find_one({"admin_id": request.app.state.admin_id, "name": name.lower()})

    if isinstance(business, dict):
        return f"business with same name exists"