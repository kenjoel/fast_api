from fastapi import FastAPI, Query, Path, Body, Cookie, Header, Form, File, UploadFile, HTTPException, Request, Depends
from typing import Optional, List, Set, Dict
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from datetime import datetime, time, timedelta

from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.responses import PlainTextResponse

description = """

ChimichangApp API helps you do awesome stuff. 🚀
## Items

You can **read items**.
## Users

You will be able to:

* **Create users** (_not implemented_).

* **Read users** (_not implemented_).

"""


app = FastAPI(

    title="ChimichangApp",

    description=description,

    version="0.0.1",

    terms_of_service="http://example.com/terms/",

    contact={

        "name": "Deadpoolio the Amazing",

        "url": "http://x-force.example.com/contact/",

        "email": "dp@x-force.example.com",

    },

    license_info={

        "name": "Apache 2.0",

        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",

    },

)

'''DOC'''

'''For Authentication'''

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

''' ENDSH HERE'''


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


@app.get("/its/{item_id}")
async def read_items(
        item_id: int = Path(..., title="The ID of the item to get"),
        q: Optional[str] = Query(None, alias="item-query"),
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


@app.put("it/{item_id}")
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


# Adding examples of the type of object to expect is indispensable to smooth structure
@app.put("/ems/{item_id}")
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


@app.put("/itms/{item_id}")
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


@app.get("/i/")
async def read_items(ads_id: Optional[str] = Cookie(None)):
    return {"ads_id": ads_id}


@app.get("/iems/")
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


'''Custom Headers'''


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


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


'''Override request validation exceptions¶'''


@app.exception_handler(RequestValidationError)
def overrideRequestValidation(request, exc):
    return PlainTextResponse(str(exc), status_code=400)


@app.get("/override}")
async def read_item(item_id: int):
    if item_id == 3:
        raise HTTPException(status_code=418, detail="Nope! I don't like 3.")
    return {"item_id": item_id}


'''ENDS HERE'''

'''PATH CONFIGURATION'''


# Deprecate a path operation


@app.get("/elements/", tags=["items"], deprecated=True, response_description="The deprecated item",
         )
async def read_elements():
    return [{"item_id": "Foo"}]


# ENDS HERE
''''''

'''Json Encoder'''

fakeDb = {}


class Transaction_data(BaseModel):
    name: str
    id: int
    time: datetime
    transaction_description: str


@app.post("/latest")
def get_func(item: Transaction_data, id: str):
    json_data = jsonable_encoder(item)
    fakeDb[id] = json_data
    return fakeDb


'''Ends Here'''

'''CLASSES AS DEPENDENCIES'''

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


class CommonQueryParams:
    def __init__(self, q: Optional[str] = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit


@app.get("/perp/")
async def perusal(commons: CommonQueryParams = Depends(CommonQueryParams)):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    running = fake_items_db[commons.skip: commons.skip + commons.limit]
    response.update({"runners": running})
    return response


'''ENDS HERE'''

'''
DEPENDS ON A SUB-DEPENDENCY'''


def query_extractor(q: Optional[str] = None):
    return q


def query_or_cookie_extractor(
        q: str = Depends(query_extractor), last_query: Optional[str] = Cookie(None)
):
    if not q:
        return last_query
    return q


@app.get("/sub_dependency/")
async def read_query(query_or_default: str = Depends(query_or_cookie_extractor)):
    return {"q_or_cookie": query_or_default}


'''ENDS HERE'''

'''LIST OF DEPENDENCIES'''


async def verify_token(x_token: str = Header(...)):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: str = Header(...)):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key


@app.get("/items/", dependencies=[Depends(verify_token), Depends(verify_key)])
async def read_items():
    return [{"item": "Foo"}, {"item": "Bar"}]


# BY DOING THIS:
# app = FastAPI(dependencies=[Depends(verify_token), Depends(verify_key)])
# You add the dependancies to the whole application


'''ENDS HERE'''

'''CONTEXT MANAGERS'''


# these are verbs used with 'with'
# you can create your own using FASTAPI

class DBSession:
    def close(self):
        pass


class MySuperContextManager:
    def __init__(self):
        self.db = DBSession()

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.close()


async def get_db():
    with MySuperContextManager() as db:
        yield db


'''ENDS HERE'''

'''AUTH2 Authentication and Authorization'''


@app.get("/authenticate")
async def authenticate(token: str = Depends(oauth2_scheme)):
    return {"token": token}


def fake_decode_token(token):
    return User(
        username=token + "fakedecoded", email="john@example.com", full_name="John Doe"
    )


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    return user


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


'''ENDS HERE'''
