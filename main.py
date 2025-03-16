from flask import Flask
from src.routes.authentication_routes import authentication_routes

app = Flask(__name__)

# [routes] authentication
app.register_blueprint(authentication_routes)

if __name__ == '__main__':
    app.run(debug=True)