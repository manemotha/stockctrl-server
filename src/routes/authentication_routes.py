from flask import Blueprint, request, current_app
import json
import bcrypt
import uuid
from src.utils.input_handler import *
from schema import Schema, And, Use, Optional

authentication_routes = Blueprint("authentication_routes", __name__)

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
        return {"error":f"{error}"}
    
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
        return {"error": f"invalid user data: {error}"}
    
    # get mongodb-database connection from app.extensions
    # app.extension exposed in main.py
    mongodb_connection = current_app.extensions['pymongo']
    
    # TODO: mongodb-database connection error handling
    
    # [ensure] username is valid
    username_validation_result = validate_username(user_data["username"])
    if username_validation_result != "valid username":
        return username_validation_result
    
    # check if username already exists
    if mongodb_connection.db.profiles.find_one({"username":user_data["username"]}):
        return {"error": "account with same username exists"}
    
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
            return {"error": f"database error: {error}"}
        
        return {"response":"account generated"}
    
    else:
        return pwd_validation_result