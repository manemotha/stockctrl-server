from flask import Blueprint, request
from pymongo import MongoClient
import pymongo
import json
import bcrypt
import uuid
from src.config import MONGODB_SERVER_URI
from src.utils.validation import *

authentication_routes = Blueprint("authentication_routes", __name__)

@authentication_routes.route('/authentication/signup', methods=['POST'])
def signup():
    """Generate a user account.
    
    Data is sent in JSON format. The JSON data should include the following:
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
    Return: user profile data from database in JSON format.
    """
    
    # handle data from request
    try:
        user_data = json.loads(request.data)
    except json.decoder.JSONDecodeError as error:
        return {"error":f"{error}"}
    
    # [ensure] user_data contains required keys
    try:
        user_data = {
            "_id": uuid.uuid4().hex,
            "username": user_data["username"],
            "email": user_data["email"],
            "password": user_data["password"],
            "name": user_data["name"],
            "organization": {
                "name": user_data["organization"]["name"],
                "type": user_data["organization"]["type"],
                "industry": user_data["organization"]["industry"],
            }    
        }
    except KeyError:
        return {"error": "missing required keys"}
    
    # mongodb-database connection
    mongodb_connection = MongoClient(MONGODB_SERVER_URI, serverSelectionTimeoutMS=500)
        
    # handle mongodb-database connection error
    try:
        mongodb_connection.server_info()
    except pymongo.errors.ConnectionFailure:
        return {"result": "failed connecting to mongodb-database"}
    
    # [ensure] username is valid
    username_validation_result = validate_username(user_data["username"])
    if username_validation_result != "valid username":
        return username_validation_result
    
    # check if username already exists
    if mongodb_connection.stockctrl.profiles.find_one({"username":user_data["username"]}):
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
            mongodb_connection.stockctrl.profiles.insert_one(user_data)
            
            # close mongodb-database connection
            mongodb_connection.close()
            
        except:
            return {"error": "failed inserting object into mongodb-database"}
        
        return {"response":"account generated"}
    
    else:
        return pwd_validation_result