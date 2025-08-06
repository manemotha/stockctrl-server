from fastapi import Request
from core.formatters import iso_format_datetime
from bson import ObjectId, errors as bson_error
from typing import Any


async def get_business(request: Request, business_id: str) -> None | dict[str, Any]:
    """
    Retrieve business data by ID.

    :param request: Request object.
    :param business_id: The ID of the business to retrieve.
    :return: A dictionary with business data.
    :raises ValueError: If the business_id is invalid or does not exist.
    """
    try:
        query = {
            '_id': ObjectId(business_id),
            'admin_id': request.app.state.admin_id
        }
    except bson_error.InvalidId:
        raise ValueError("invalid business_id")

    # MONGODB: assign businesses collection/table
    businesses_table = request.app.state.mongo_database["businesses"]

    # MONGODB: projection to return only necessary fields.
    # fields not mentioned here will not be returned and
    # _id is included by default
    projection = {
        'name': True,
        'name_lower': True,
        'type': True,
        'phone_number': True,
        'currency': True,
        'timezone': True,
        'location': True,
        'is_active': True,
        'created_at': True
    }

    # MONGODB: find business with matching admin_id & business_id
    business_db_data = await businesses_table.find_one(query, projection)

    # ENSURE: business is a dictionary
    if isinstance(business_db_data, dict):

        # Serialize ObjectId to string for JSON compatibility
        business_db_data["_id"] = str(business_db_data["_id"])

        # ISO format datetime
        business_db_data["created_at"] = iso_format_datetime(business_db_data["created_at"])

        return business_db_data
    else:
        raise ValueError("invalid business_id")


async def get_businesses(request: Request) -> None | list[dict[str, Any]]:
    """
    Retrieve all user businesses.

    :param request: Request object.
    :return: A dictionary with businesses data.
    :return: A dictionary businesses data or None if no businesses exist.
    """
    # MONGODB: assign businesses collection/table
    businesses_table = request.app.state.mongo_database["businesses"]

    # MONGODB: projection to return only necessary fields.
    # fields not mentioned here will not be returned and
    # _id is included by default
    projection = {
        'name': True,
        'name_lower': True,
        'type': True,
        'phone_number': True,
        'currency': True,
        'timezone': True,
        'location': True,
        'is_active': True,
        'created_at': True
    }

    # MONGODB: find business with matching admin_id & business_id
    businesses_db_data = await businesses_table.find({
        'admin_id': request.app.state.admin_id
    }, projection).to_list(length=None)

    # Serialize ObjectId to string for JSON compatibility
    result_businesses = []
    for business in businesses_db_data:
        if isinstance(business, dict):

            # ISO format datetime
            business["created_at"] = iso_format_datetime(business["created_at"])

            # Serialize ObjectId to string for JSON compatibility
            business["_id"] = str(business["_id"])

            # Append business into result businesses
            result_businesses.append(business)

    # ENSURE: at least one business exists
    if len(result_businesses) == 0:
        return None

    return result_businesses