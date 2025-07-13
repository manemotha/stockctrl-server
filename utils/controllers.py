from typing import Any
from fastapi.responses import JSONResponse


def http_response(message: str, status_code: int) -> JSONResponse | tuple[Any, int]:
    """
    Generate a JSON HTTP response with a custom message and status code.

    :param message: The message to include in the response body.
    :param status_code: The HTTP status code for the response.

    :returns: A FastAPI JSONResponse object with the given message and status code. If an error occurs, returns a JSONResponse with the error message and a 500 status code.
    """
    try:
        return JSONResponse(content={"message": message}, status_code=status_code)
    except TypeError as error:
        return JSONResponse(content={"message": error}, status_code=500)