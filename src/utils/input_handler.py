from flask import current_app, session


def validate_password(password: str):
    """
    # Validate Password
    Ensure password is valid and meets **SC** requirements.

    **Keyword arguments:**  
    Password : Is the string to validate (str)
    
    Return: `True` or `"error": validation error massage`
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

def validate_username(username: str):
    """
    # Validate Username
    Ensure username is valid and meets **SC** requirements.
    
    **Keyword arguments:**  
    username : is the string to validate (str)
    
    Return: `"valid username"` or `"error": validation error massage`
    """
    
    # [ensure] username is type:string
    if type(username) is not str:
        username = str(username)
    
    # [ensure] username meets requirements
    if len(username) >= 5:
        
        # [ensure] username maximum number of characters allowed is 30 chars
        if len(username) > 30:
            return {"error": "username maximum number of characters allowed is 30 chars"}
        
        # [ensure] username contains only lowercase letters, digits, underscores, and periods
        if not username.islower() or not all(char.isalnum() or char in '._' for char in username):
            return {"error": "username must be lowercase and can only contain letters, digits, underscores, and periods (._)"}
        
        # [ensure] username does not begin or end with symbols
        if username[0] in '._' or username[-1] in '._':
            return {"error": "username cannot begin or end with special characters (._)"}
        
        return "valid username"
    else:
        return {"error": "username minimum number of characters required is 5 chars"}

def validate_session_token(f):
    """
    ## Ensure token authorization to sensitive routes.
    
    Decorator function called before secured routes that demands  
    token authentication.
    
    **Usage Example:**
    > `@authentication_routes.route('/login', methods=['POST'])`  
    > -> `@validate_session_token`  
    > `def login():`
    
    Return: `"valid token"` or `"invalid token"`
    """
    def decorated_function(*args, **kwargs):
        # get mongodb-database connection from app.extensions
        # app.extension exposed in main.py
        mongodb_connection = current_app.extensions['pymongo']
        
        try:
            # assign session data to variables
            username = session['username']
            session_token = session['token']
            
        except KeyError:
            return {'error': 'invalid session token'}
        
        # find user with matching session_token from database
        user_db_data = mongodb_connection.db.profiles.find_one(
            {"username": username, "sessions_token": {"$elemMatch": {"$eq": session_token}}}
        )
        
        # if user is not in database
        if not user_db_data or not isinstance(user_db_data, dict):
            # remove username and token from user cookies
            session.pop('username', None)
            session.pop('token', None)
            # function called from sensitive route
            return {'error': 'invalid session token'}
        
        # token is valid, proceed to the targeted route
        return f(*args, **kwargs)
    
    return decorated_function