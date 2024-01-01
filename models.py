from bson import ObjectId
from pydantic import Field, BaseModel, ConfigDict
from typing import Optional, Annotated
from pydantic.functional_validators import BeforeValidator

# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]


class MongoBaseModel(BaseModel):
    # The primary key for the MongoBaseModel, stored as a `str` on the instance.
    # This will be aliased to `_id` when sent to MongoDB,
    # but provided as `id` in the API requests and responses.
    id: Optional[PyObjectId] = Field(alias="_id", default=None)


class CarModel(MongoBaseModel):
    brand: str = Field(..., min_length=3)
    make: str = Field(..., min_length=3)
    year: int = Field(..., gt=1975, lt=2023)
    price: int = Field(...)
    km: int = Field(...)
    cm3: int = Field(...)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "brand": "Ford Doe",
                "make": "Mondeo",
                "year": 2020,
                "km": 200000,
                "price": 15000,
                "cm3": 2000,
            }
        },
    )


class CarUpdate(MongoBaseModel):
    price: Optional[int] = None
