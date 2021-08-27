from fastapi import FastAPI, Query, Path, Body, Cookie, Header, Form, File, UploadFile, HTTPException, Request
from typing import Optional, List, Set, Dict
from uuid import UUID
from datetime import datetime, time, timedelta
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from fastapi.responses import HTMLResponse, JSONResponse


app = FastAPI()


class user_base_model(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None


class UserIn(user_base_model):
    password: str


class UserOut(user_base_model):
    pass


class UserInDB(user_base_model):
    hashed_password: str


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
items = {
    "foo": {"name": "Password", "password": "kitenge", "email": "myemail@gmail.com", "full_name": "Password Kitenge"},
    "ntoa": {"name": "Nyoa", "password": "kitenge", "email": "nyemail@gmail.com", "full_name": "Nyoa Kitenge"},
    "nyoa": {"name": "Ntoa", "password": "kitenge", "email": "nemail@gmail.com", "full_name": "Ntoa Kitenge"},
}

'''
The Idea is that you can return a response model of a list of objects
'''


# @app.get("/beautiful/", response_model=List[Item])
# async def read_items():
#     return items


@app.post("/pressure/", response_model=UserIn)
async def create_users(user: UserIn):
    return user


@app.post("/user/", response_model=UserOut, response_model_exclude_unset=True)
async def create_kwangu(user: UserIn):
    return user


def lets_hash_user(rawstring: str):
    return "I will use a cryptographic algorithm" + rawstring


def lets_get_user_data(user_in: UserIn):
    hashed_password = lets_hash_user(user_in.password)
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
    return user_in_db


@app.post("/create_user")
def created_user(usr: UserIn):
    user_to_save = lets_get_user_data(usr)
    # Save user to Database
    print("Success")
    return user_to_save


@app.post("/login")
def expect_form_data(username: str = Form(..., media_type="application/x-www-form-urlencoded"),
                     password: str = Form(..., media_type="application/x-www-form-urlencoded")):
    return {"Username": username}


'''
ALL ABOUT FILE UPLOAD 
'''


@app.post("/files/")
def getFileBytes(file: bytes = File(...)):
    return {"file_size": len(file)}


@app.post("/uploadFile/")
def upload_file(file: UploadFile = File(...)):
    return {"file": file.filename}


@app.post("/uploadbyteslist")
def upload_bytes_list(files: List[bytes] = File(...)):
    return {"Your Shit": [len(file) for file in files]}


@app.post("/upload_files")
def upload_files(files: List[UploadFile] = File(...)):
    return {"filenames": [file.filename for file in files]}


@app.get("/mtaa")
async def main():
    content = """
<body>
<form action="/uploadbyteslist/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/upload_files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)


@app.post("/file&form/")
async def creator_of_files(
        file: bytes = File(...), fileb: UploadFile = File(...), token: str = Form(...)
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }


'''ENDS HERE'''

'''
ALL ABOUT ERROR HANDLING
'''


@app.get("/arap/{item_id}")
async def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item": items[item_id]}


stuff = {"foo": "The Foo Wrestlers"}


@app.get("/items-header/{item_id}")
async def read_item_header(item_id: str):
    if item_id not in stuff:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "There goes my error"},
        )
    return {"item": stuff[item_id]}


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


app = FastAPI()


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )


@app.get("/unicorns/{name}")
async def read_unicorn(name: str):
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}

'''ENDS HERE'''
