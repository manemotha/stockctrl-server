from typing import Optional
from pydantic import BaseModel, Field, EmailStr, constr


class CreateBusinessModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=20)
    type: str = Field(..., min_length=1, max_length=50)
    email: Optional[EmailStr] = Field(None)
    phone_number: Optional[str] = Field(None, min_length=10, max_length=100)
    location: Optional[str] = Field(None, min_length=1, max_length=100)
    currency: Optional[str] = Field("ZAR", max_length=3)
    timezone: Optional[str] = Field("UTC", max_length=100)

    # Forbid any extra fields in the request
    class Config:
        extra = "forbid"