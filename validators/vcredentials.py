def validate_password(password: str) -> str:
    """
    Ensure password is valid and meets authentication requirements.

    :param password: The password to validate.
    :returns: "valid password" if the password meets all requirements, otherwise a validation error message (str)
    """

    # ensure user:password meets requirements
    if len(password) >= 8:
        # [ensure] password contains symbols, digit and upper letters
        has_upper = any(char.isupper() for char in password)
        has_lower = any(char.islower() for char in password)
        has_digit = any(char.isdigit() for char in password)
        has_symbol = any(not char.isalnum() for char in password)

        if not (has_upper and has_lower and has_digit and has_symbol):
            return "password must contain uppercase letter, lowercase letter, digit, and symbols"
        return "valid password"
    else:
        return "password minimum number of characters required is 8 chars"


def validate_username(username: str) -> str:
    """
    Ensure username is valid and meets **SC** requirements.

    :param username: The username to validate.
    :returns: "valid username" if the username meets all requirements, otherwise a validation error message (str)
    """

    # [ensure] username is type:string
    if type(username) is not str:
        username = str(username)

    # [ensure] username meets requirements
    if len(username) >= 5:

        # [ensure] username maximum number of characters allowed is 30 chars
        if len(username) > 30:
            return "username maximum number of characters allowed is 30 chars"

        # [ensure] username contains only lowercase letters, digits, underscores, and periods
        if not username.islower() or not all(char.isalnum() or char in '._' for char in username):
            return "username must be lowercase and can only contain letters, digits, underscores, and periods (._)"

        # [ensure] username does not begin or end with symbols
        if username[0] in '._' or username[-1] in '._':
            return "username cannot begin or end with special characters (._)"

        return "valid username"
    else:
        return "username minimum number of characters required is 5 chars"