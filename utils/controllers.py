from typing import Any
from fastapi.responses import JSONResponse


def http_response(message: str, status_code: int) -> JSONResponse | tuple[Any, int]:
    """
    Generate a response object with the specified status code and response data.

    **Args:**
    message (str): The response data to be sent to the mongo_client.
    status_code (int): The HTTP status code to be included in the response.

    **Returns:**
    message: A Flask Response object containing the response data and status code.
    """
    try:
        return JSONResponse(content={"message": message}, status_code=status_code)
    except TypeError as error:
        return JSONResponse(content={"message": error}, status_code=500)