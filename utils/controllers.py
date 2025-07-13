from fastapi.responses import JSONResponse


def http_response(message: str, status_code: int) -> JSONResponse:
    """
    Generate a JSON HTTP response with a custom message and status code.

    :param message: The message to include in the response body.
    :param status_code: The HTTP status code for the response.

    :returns: A FastAPI JSONResponse object with the given message and status code.
    """
    return JSONResponse(content={"message": message}, status_code=status_code)