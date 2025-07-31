from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes.admin import admin_routes
from routes.employee import employee_routes
from pymongo import AsyncMongoClient
from uvicorn import run
import os

@asynccontextmanager
async def lifespan(_: FastAPI):
    # [SERVER STARTUP]
    # Init: the MongoDB client with the URI from .env variables
    # The .env file contains default MONGO_URI="mongodb://localhost:27017"
    # Replace variable with your own custom MONGODB URI
    mongo_client = AsyncMongoClient(os.environ.get("MONGO_URI"), tz_aware=True)

    # Store MongoDB client & database into FastAPI application state
    app.state.mongo_client = mongo_client # client
    app.state.mongo_database = mongo_client["stockctrl"] # database
    # [END OF SERVER STARTUP]
    yield

    # [SERVER SHUTDOWN]
    # Close the MongoDB mongo_client when the application shuts down
    await mongo_client.close()


# Init: FastAPI application
app = FastAPI(
    title="Stockctrl Server",
    description="A robust stock management solution designed to streamline inventory operations.",
    lifespan=lifespan,
    tz_aware=True,
)

# Assign server routes
app.include_router(admin_routes, prefix="/api/admin", tags=["admin"])
app.include_router(employee_routes, prefix="/api/employee", tags=["employee"])

if __name__ == "__main__":
    run("main:app", host="localhost", port=8000, reload=True)