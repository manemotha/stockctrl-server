from fastapi import Request
from datetime import datetime, timezone, timedelta
import secrets
import bcrypt
from bson import ObjectId


def generate_auth_token() -> dict[str, str | datetime]:
    """
    Generate authentication token with an expiration date.

    **Return:**
     token (str)\n
     expires_at (datetime)
    """
    token = secrets.token_urlsafe(64)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    return {"token":token, "expires_at":expires_at}


async def revoke_auth_token(request: Request, token: str):
    """
    Revoke a session token by setting its 'revoked' status to True.

    **Args:**
     token (str)\n
     request (FastAPI Request)
    """
    # MongoDB: assign auth_tokens collection/table
    auth_tokens_table = request.app.state.mongo_database["session_tokens"]

    # MongoDB: set session_token revoked to true
    await auth_tokens_table.update_one(
        {"token": token},
        {"$set": {"revoked": True, "revoked_at": datetime.now(timezone.utc)}}
    )


async def replace_admin_auth_token(request: Request, employee_id: ObjectId):
    """
    Override admin token with employee token for future requests.
    Current session is now authorized to the employee.

    **Args:**
     request (FastAPI Request)
     admin_token (str) : The token for which to replace.
    """
    # MongoDB: assign auth_tokens collection/table
    session_tokens_table = request.app.state.mongo_database["session_tokens"]

    # MongoDB: set session_token replaced to true
    await session_tokens_table.update_one(
        {"token": request.app.state.token},
        {"$set": {"is_replaced": True, "replaced_by": employee_id, "replaced_at": datetime.now(timezone.utc)}}
    )


def hash_password(password: str) -> bytes:
    """
    Generate hashed password

    **Args:**
     password (str):

    **Return:**
     (bytes) bcrypt hashed password
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def compare_hashed_password(password: str, hashed_password: bytes) -> bool:
    """
    Compare a password with a hashed password.

    **Args:**
     password (str): The plain text password to compare.\n
     hashed_password (bytes): The hashed password to compare against.

    **Return:**
     (bool) True | False
    """
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)