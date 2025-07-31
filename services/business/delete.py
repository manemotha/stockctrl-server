from fastapi import Request
from validators.vbusiness import check_business_exists
from bson import ObjectId


async def delete_business(request: Request, business_id: str) -> None:
    """
    Delete business data by ID.

    :param request: Request object.
    :param business_id: The ID of the business to delete.
    :raise ValueError: If the business_id is invalid or does not exist.
    """
    # MONGODB: assign businesses collection/table
    businesses_table = request.app.state.mongo_database["businesses"]

    try:
        # ENSURE: business exists
        await check_business_exists(business_id, request)

        # MONGODB: delete business with matching business_id
        await businesses_table.delete_one({"_id": ObjectId(business_id)})
    except ValueError as error:
        raise ValueError(error)