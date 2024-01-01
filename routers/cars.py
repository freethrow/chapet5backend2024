from typing import List, Optional

from fastapi import APIRouter, Request, Body, status, HTTPException, Response

from bson import ObjectId
from pymongo import ReturnDocument

from models import CarModel, CarUpdate

# solution adapted to match the MongoDB documentation and quickstart from:
# https://www.mongodb.com/developer/languages/python/python-quickstart-fastapi/

router = APIRouter()


@router.get(
    "/",
    response_description="List all cars",
    response_model=List[CarModel],
    response_model_by_alias=False,
)
async def list_students(request: Request):
    """
    List all of the student data in the database.

    The response is unpaginated and limited to 1000 results.
    """

    cars = await request.app.state.mongodb["cars2024"].find().to_list(1000)

    results = [CarModel(**raw_car) for raw_car in cars]

    return results


# create new car
@router.post(
    "/",
    response_description="Add new car",
    response_model=CarModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_car(request: Request, car: CarModel = Body(...)):
    """
    "brand":"Ford",
    "make":"Mondeo",
    "year":2020,
    "price":3039,
    "km":102000,
    "cm3":1900
    """
    new_car = await request.app.state.mongodb["cars2024"].insert_one(
        car.model_dump(by_alias=True, exclude=["id"])
    )
    created_car = await request.app.state.mongodb["cars2024"].find_one(
        {"_id": new_car.inserted_id}
    )
    return created_car


# get car by ID
@router.get("/{id}", response_description="Get a single car")
async def show_car(id: str, request: Request):
    if (
        car := await request.app.state.mongodb["cars2024"].find_one(
            {"_id": ObjectId(id)}
        )
    ) is not None:
        return CarModel(**car)
    raise HTTPException(status_code=404, detail=f"Car with {id} not found")


# update car by ID
@router.put(
    "/{id}",
    response_description="Update a car",
    response_model=CarModel,
    response_model_by_alias=False,
)
async def update_car(id: str, request: Request, car: CarUpdate = Body(...)):
    """
    Update individual fields of an existing car record.

    Only the provided fields will be updated.
    Any missing or `null` fields will be ignored.

    In our case only the price will be updated.
    """
    car = {k: v for k, v in car.model_dump(by_alias=True).items() if v is not None}

    if len(car) >= 1:
        update_result = await request.app.state.mongodb["cars2024"].find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": car},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"Car with id: {id} not found")

    # The update is empty, but we should still return the matching document:
    if (
        existing_car := await request.app.state.mongodb["cars2024"].find_one(
            {"_id": id}
        )
    ) is not None:
        return existing_car

    raise HTTPException(status_code=404, detail=f"Car with id: {id} not found")


@router.delete("/{id}", response_description="Delete a car")
async def delete_car(id: str, request: Request):
    """
    Remove a single car record from the database.
    """
    delete_result = await request.app.state.mongodb["cars2024"].delete_one(
        {"_id": ObjectId(id)}
    )

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Car with id {id} not found")
