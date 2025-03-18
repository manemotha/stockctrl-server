from flask import Flask
from flask_pymongo import PyMongo
from src.routes.authentication_routes import authentication_routes
from src.config import DEBUG_ENABLED, MONGODB_SERVER_URI

def create_app():
    """
    Create and configure the Flask application.
    """
    app = Flask(__name__)
    app.config['DEBUG'] = DEBUG_ENABLED
    app.config['MONGO_URI'] = MONGODB_SERVER_URI
    
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