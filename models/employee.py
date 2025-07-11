from typing import Optional
from pydantic import BaseModel, Field, EmailStr, constr


class EmployeeSignupModel(BaseModel):
    username: str = Field(..., min_length=1, max_length=20)
    password: str
    business_id: str = Field(..., min_length=1, max_length=50)
    email: Optional[EmailStr] = Field(None)
    phone_number: Optional[str] = Field(None, min_length=10)

    # Forbid any extra fields in the request
    class Config:
        extra = "forbid"


class EmployeeSigninModel(BaseModel):
    username: constr(to_lower=True)
    password: str = Field(..., min_length=8, max_length=128)

    # Forbid any extra fields in the request
    class Config:
        extra = "forbid"