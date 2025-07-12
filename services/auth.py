from fastapi import Request
from datetime import datetime, timezone, timedelta
import secrets
import bcrypt
from bson import ObjectId


def generate_auth_token() -> dict[str, str | datetime]:
    """
    Generate authentication token with an expiration date.

    :returns: A dictionary containing token and its expiration date.
    """
    token = secrets.token_urlsafe(64)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    return {"token":token, "expires_at":expires_at}


async def revoke_auth_token(request: Request, token: str):
    """
    Revoke a session token by setting its 'revoked' status to True.

    :param request: FastAPI request object.
    :param token: Authentication token for which to revoke.
    :returns: None
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
    The current session is now authorized to the employee.

    :param request: FastAPI request object.
    :param employee_id: The employee id for which to replace admin token with.
    :returns: None
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
    Generate hashed password.

    :param password: The string to hash.
    :returns: The hashed password as bytes.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def compare_hashed_password(password: str, hashed_password: bytes) -> bool:
    """
    Compare a password with a hashed password.

    :param password: The string password to compare.
    :param hashed_password: The hashed password to compare against.
    :returns: True if the password matches the hashed password, otherwise False.
    """
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)