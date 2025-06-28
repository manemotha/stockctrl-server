from typing import Optional
from pydantic import BaseModel, Field, EmailStr, constr


# Define the model for creating an admin user
class AdminSignupModel(BaseModel):
    username: constr(to_lower=True)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, min_length=10, max_length=100)

    # Forbid any extra fields in the request
    class Config:
        extra = "forbid"