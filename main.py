from flask import Flask
from src.routes.authentication_routes import authentication_routes
from src.config import DEBUG_ENABLED

def create_app():
    """
    Create and configure the Flask application.
    """
    app = Flask(__name__)
    app.config['DEBUG'] = DEBUG_ENABLED

    # Register blueprints
    app.register_blueprint(authentication_routes)

    return app

if __name__ == '__main__':
    app = create_app()
    # Run the application
    app.run()