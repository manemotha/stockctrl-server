from fastapi import FastAPI
from contextlib import asynccontextmanager
from db import mongo_client
from routes.admin import admin_routes
from uvicorn import run


@asynccontextmanager
async def lifespan(_: FastAPI):

    # Store MongoDB client & database into FastAPI application state
    app.state.mongo_client = mongo_client # client
    app.state.mongo_database = mongo_client["stockctrl"] # database
    yield

    # Close the MongoDB mongo_client when the application shuts down
    await mongo_client.close()


# Init: FastAPI application
app = FastAPI(
    title="Stockctrl Server",
    description="A robust stock management solution designed to streamline inventory operations.",
    lifespan=lifespan,
    tz_aware=True,
)

# Declare server routes
app.include_router(admin_routes, prefix="/api/admins", tags=["admins"])

if __name__ == "__main__":
    run("main:app", host="localhost", port=8000, reload=True)