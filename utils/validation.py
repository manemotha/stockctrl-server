from __init__ import *


def validate_password(password: str):
    """
    Ensure password is valid and meets SC requirements.
    
    Keyword arguments:
    password -- is the user password to validate (string)
    
    Return: True || dict "error": validation error massage
    """
    
    # ensure user:password meets requirements
    if len(password) >= 8:
        # [ensure] password contains symbols, digit and upper letters
        has_upper = any(char.isupper() for char in password)
        has_lower = any(char.islower() for char in password)
        has_digit = any(char.isdigit() for char in password)
        has_symbol = any(not char.isalnum() for char in password)
        
        if not (has_upper and has_lower and has_digit and has_symbol):
            return {"error": "password must contain uppercase letter, lowercase letter, digit, and symbols"}
        return "valid password"
    else:
        return {"error": "password minimum number of characters required is 8 chars"}