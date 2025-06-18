"""
This module is used for streamlining operations within the application.

It provides utility functions, classes, or configurations that enhance 
the efficiency and maintainability of the application's core processes. 
The functionalities implemented in this file are designed to simplify 
complex workflows, reduce redundancy, and improve overall performance.

Usage:
    Import this module to access streamlined operations and utilities 
    for the application.

Note:
    Ensure that all dependencies are properly installed and configured 
    before using this module.
"""
from flask import jsonify, Response

def http_response(message: str, status_code: int) -> Response:
    """
    Generate a response object with the specified status code and response data.

    Args:
        message (str): The response data to be sent to the client.
        status_code (int): The HTTP status code to be included in the response.

    Returns:
        Response: A Flask Response object containing the response data and status code.
    """
    try:
        return jsonify({"message": message}), status_code
    except TypeError as e:
        return jsonify({"message": str(e)}), 500