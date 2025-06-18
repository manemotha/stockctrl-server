from flask import Blueprint, request
import json
import bcrypt
import uuid
from src.utils.input_handler import *
from schema import Schema, And, Use, Optional
from src.utils.controllers import http_response
import asyncio

# create authentication_routes blueprint
# this blueprint will be registered in "main.py"
# and will expose the routes defined in this file
# to the main application
authentication_routes = Blueprint("authentication_routes", __name__)

@authentication_routes.route('/authentication/session_token/validate', methods=['GET'])
@validate_session_token
def validate_token():
    """
    # Validate Token
    **Validate user token**.
    
    Return: `"response": "valid token"`
    """
    return http_response(message="Valid token", status_code=200)

@authentication_routes.route('/authentication/signup', methods=['POST'])
def signup():
    """
    # Signup
    **Generate user account**.
    
    Request data is sent in containing the following keys:
    - username:
    - email:
    - password:
    - name:
    - phone_number: (optional)
    - organization: {
        - name:
        - type:
        - industry:
        - logo: (optional)
    }
    
    Return: `"response": "account generated"`
    """
    
    # handle data from request
    try:
        user_data = json.loads(request.data)
    except json.decoder.JSONDecodeError as error:
        return http_response(message=str(error), status_code=400)
    
    # Define schema for user data validation
    user_schema = Schema({
        'username': And(str, len, Use(str.lower)),
        'email': And(str, len),
        'password': And(str, len),
        'name': And(str, len),
        Optional('phone_number', default=""): And(str, len),
        'organization': {
            'name': And(str, len),
            'type': And(str, len),
            'industry': And(str, len),
            Optional('logo', default=""): And(str, len)
        }
    }, ignore_extra_keys=False)

    # Validate user data
    try:
        result = user_schema.validate(user_data)
        user_data = result
        
        # generate user UUID
        user_data["_id"] = str(uuid.uuid4())
    except Exception as error:
        return http_response(message=str(error), status_code=400)
    
    # get mongodb-database connection from app.extensions
    # app.extension exposed in main.py
    mongodb_connection = current_app.extensions['pymongo']
    
    # TODO: mongodb-database connection error handling
    
    # [ensure] username is valid
    username_validation_result = validate_username(user_data["username"])
    if username_validation_result != "valid username":
        return http_response(message=username_validation_result["error"], status_code=400)
    
    # check if username already exists
    if mongodb_connection.db.profiles.find_one({"username":user_data["username"]}):
        return http_response(message="Account with this username already exists", status_code=400)
    
    # [ensure] password is type:string
    user_password = user_data["password"]
    if type(user_password) is not str:
        user_password = str(user_password)
    
    # [ensure] password meets requirements
    pwd_validation_result = validate_password(user_password)
    
    if pwd_validation_result == "valid password":
            
        # encrypt user password
        hashed_password: bytes = bcrypt.hashpw(user_password.encode("utf-8"), bcrypt.gensalt())
        
        # insert handshed password into prepared user_data
        user_data["password"] = hashed_password
        
        # handle error when inserting data into database
        try:
            # insert user_data into mongodb-database
            mongodb_connection.db.profiles.insert_one(user_data)
        except Exception as error:
            return http_response(message=str(error), status_code=500)
        
        return {"response":"account generated"}
    
    else:
        return http_response(message=pwd_validation_result, status_code=400)

@authentication_routes.route('/authentication/login', methods=['POST'])
async def login():
    """
    # Login
    **Authenticate user and generate login token**.
    
    Request data is sent in containing the following keys:
    - username:
    - password:
    
    Return: `"response": "login successful"` and generate a token in user cookies
    """

    # handle data from request
    try:
        user_login_data = json.loads(request.data)
    except json.decoder.JSONDecodeError as error:
        return http_response(message=str(error), status_code=400)
    
    # define schema for login data validation
    user_schema = Schema({
        'username': And(str, len, Use(str.lower)),
        'password': And(str, len)
    }, ignore_extra_keys=False)
    
    # validate login data
    try:
        result = user_schema.validate(user_login_data)
        user_login_data = result
    except Exception as error:
        return http_response(message=str(error), status_code=400)
    
    # get mongodb-database connection from app.extensions
    # app.extension exposed in main.py
    mongodb_connection = current_app.extensions['pymongo']
    
    # get user data from database
    user_db_data = mongodb_connection.db.profiles.find_one({"username": user_login_data["username"]})
    
    # ensure user_db_data is valid
    if not user_db_data or not isinstance(user_db_data, dict):
        await asyncio.sleep(1.5) # delay response by 1.5 seconds
        return http_response(message="Invalid username or password", status_code=401)
    
    # compare user password with hashed password
    if bcrypt.checkpw(user_login_data["password"].encode("utf-8"), user_db_data["password"]):
        
        # generate user token
        session_token = str(uuid.uuid4())
        
        # store user token in database
        # token is unique for each user session
        mongodb_connection.db.profiles.update_one(
            {"username": user_login_data["username"]},
            {"$addToSet": {"sessions_token": {"$each": [session_token]}}},
            upsert=True
        )

        # add session_token and username to user session cookies
        session["token"] = session_token
        session["username"] = user_login_data["username"]

        return http_response(message="Login successful", status_code=200)
    else:
        await asyncio.sleep(1.5) # delay response by 1.5 seconds
        return http_response(message="Invalid username or password", status_code=401)