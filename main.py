from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from flask_pymongo import PyMongo
from src.routes.authentication_routes import authentication_routes
from src.config import DEBUG_ENABLED, MONGODB_SERVER_URI, SECRET_KEY

def create_app():
    """
    Create and configure the Flask application.
    """
    app = Flask(__name__)
    app.config['DEBUG'] = DEBUG_ENABLED
    app.config['MONGO_URI'] = MONGODB_SERVER_URI
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config.from_object(Config)
    JWTManager(app)

    # Uncomment the line below to enable CORS for specific origins.
    # replace URL with your client-URL.
    # CORS(app, origins=["https://stockctrl-client.example.com"], supports_credentials=True)

    CORS(app) # Enable CORS for all routes, development/testing purposes.
    
    # register the mongo instance to the app
    mongo = PyMongo(app)
    # expose the mongo instance to the app
    app.extensions['pymongo'] = mongo

    # Register blueprints
    app.register_blueprint(authentication_routes)

    return app

if __name__ == '__main__':
    app = create_app()
    # Run the application
    app.run()