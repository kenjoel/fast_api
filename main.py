import ssl

from fastapi import FastAPI, Query, Path, Body, Cookie, Header
from typing import Optional, List, Set, Dict
from uuid import UUID
from datetime import datetime, time, timedelta
from pydantic import BaseModel, Field, HttpUrl, EmailStr

app = FastAPI()


class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: Optional[str] = None


class Kitenge(BaseModel):
    name: str
    desc: str
    price: float
    tax: Optional[float]

    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            }
        }


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    description: Optional[str] = Field(None, title="This is the description", max_length=100)
    price: float = Field(None, description="Must be greater than 0.0")
    tax: Optional[float] = None
    availability = bool
    tags: List[str] = []
    taps: Set[str] = set()
    # exp: Dict[str] = {}
    image: Optional[List[Image]] = None


class User(BaseModel):
    user_name: str
    role: bool


class Offer(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    items: List[Item]


@app.post("/offers/")
async def post_items_on_offer(offer: Offer):
    return offer


@app.get("/")
def see_this():
    return {"Hello": "World"}


@app.get("/item/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {item_id: "item_id", "q": q}


@app.post("/create/")
async def create_item(item: Item):
    obj = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        obj.update({"price_with_tax": price_with_tax})
    return item


# @app.put("update/{item_id}")
# def update_item(item_id: int, item: Item):
#     return {"item_id": item_id, "Item": Item.dict()}


@app.get("/items/")
async def read_items(
        q: Optional[str] = Query(None, min_length=3, max_length=50, regex="^fixedquery$")
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


@app.get("/items/{item_id}")
async def read_items(
        item_id: int = Path(..., title="The ID of the item to get"),
        q: Optional[str] = Query(None, alias="item-query"),
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


@app.put("items/{item_id}")
async def update_user(item_id: int, user: User, item: Item):
    if user.role:
        print("This is an American User")
    results = {"item_id": item_id, "User": user, "Item": item}
    return results


# @app.put("/items/{item_id}")
# async def update_item(
#         *,
#         item_id: int,
#         item: Item,
#         user: User,
#         importance: int = Body(..., gt=0),
#         q: Optional[str] = None
# ):
#     results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
#     if q:
#         results.update({"q": q})
#     return results


@app.post("/images/multiple/")
async def create_multiple_images(images: List[Image]):
    return images


@app.post("/index-weights/")
async def create_index_weights(weights: Dict[int, float]):
    return weights


'''
#Start Here
https://pydantic-docs.helpmanual.io/usage/schema/#schema-customization
'''


# You can declare and example of Pydantic model using Config and Schema_extra


# Adding examples of the type of onbject to expect is indisensable to smooth structure
@app.put("/items/{item_id}")
async def update_item(
        *,
        item_id: int,
        item: Item = Body(
            ...,
            examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** item works correctly.",
                    "value": {
                        "name": "Foo",
                        "description": "A very nice Item",
                        "price": 35.4,
                        "tax": 3.2,
                    },
                },
                "converted": {
                    "summary": "An example with converted data",
                    "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                    "value": {
                        "name": "Bar",
                        "price": "35.4",
                    },
                },
                "invalid": {
                    "summary": "Invalid data is rejected with an error",
                    "value": {
                        "name": "Baz",
                        "price": "thirty five point four",
                    },
                },
            },
        ),
):
    results = {"item_id": item_id, "item": item}
    return results


@app.put("/items/{item_id}")
async def read_items(
        item_id: UUID,
        start_datetime: Optional[datetime] = Body(None),
        end_datetime: Optional[datetime] = Body(None),
        repeat_at: Optional[time] = Body(None),
        process_after: Optional[timedelta] = Body(None),
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "repeat_at": repeat_at,
        "process_after": process_after,
        "start_process": start_process,
        "duration": duration,
    }


@app.get("/items/")
async def read_items(ads_id: Optional[str] = Cookie(None)):
    return {"ads_id": ads_id}


@app.get("/items/")
async def read_items(user_agent: Optional[str] = Header(None)):
    return {"User-Agent": user_agent}


# Convert Header Underscores
@app.put("kilio/shit")
async def hurt(user_agent: Optional[str] = Header(None, convert_underscores=False)):
    return {"user_agent": user_agent}


# Response Model
@app.post("/items/stemmed", response_model=Item)
async def create_item(item: Item):
    return item


# Don't do this in production!
@app.post("/user/", response_model=UserIn)
async def create_user(user: UserIn):
    return user
