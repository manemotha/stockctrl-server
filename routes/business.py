from fastapi import APIRouter, status
from models.business import CreateBusinessModel
from services.auth import *
from validators.vadmin import validate_admin_token
from validators.vbusiness import validate_business_name
from datetime import datetime, timezone
from utils.controllers import http_response
from typing import Any

business_routes = APIRouter()


@business_routes.post("/")
@validate_admin_token()
async def create_new_business(request: Request, payload: CreateBusinessModel):

    # Read the payload and convert it to a dictionary
    business_data: dict[str, Any] = payload.model_dump()

    # Assign business name in lowercase
    business_name = business_data["name"].lower()

    # Validate: business name
    validation_result = await validate_business_name(business_name, request)
    if validation_result:
        return http_response(message=validation_result, status_code=status.HTTP_409_CONFLICT)

    # Insert system additional fields
    business_data['admin_id'] = request.app.state.admin_id
    business_data['created_at'] = datetime.now(timezone.utc)
    business_data['is_active'] = True

    # MongoDB: assign businesses collection/table
    businesses_table = request.app.state.mongo_database["businesses"]

    # MongoDB: insert new business data
    await businesses_table.insert_one(business_data)

    return http_response(message="business created", status_code=status.HTTP_201_CREATED)