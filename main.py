from fastapi import FastAPI
import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient

from contextlib import asynccontextmanager

from routers.cars import router as cars_router


from decouple import config

DB_URL = config("DB_URL", cast=str)
DB_NAME = config("DB_NAME", cast=str)

print(DB_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("This gets executed on startup!")
    app.state.mongodb_client = AsyncIOMotorClient(DB_URL)
    app.state.mongodb = app.state.mongodb_client[DB_NAME]
    print(app.state.mongodb_client)

    yield

    print("This gets executed on shutdown!")
    app.state.mongodb_client.close()


app = FastAPI(lifespan=lifespan)


app.include_router(cars_router, prefix="/cars", tags=["cars"])


# if __name__ == "__main__":
#     uvicorn.run("main:app", reload=True)
