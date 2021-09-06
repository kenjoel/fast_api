from fastapi import APIRouter, Depends

from main import UnicornException

router = APIRouter()


@router.post("/create")
def create_whatever(user: object):
    return {"User": user}


@router.get("/read/users")
async def read_users():
    return [{"user": "Rick Sanchez"}, {"user1": "Morty"}]


'''We can also be subtle with it like this'''

brouter = APIRouter(
    prefix="items",
    tags=["items"],
    dependencies=[Depends(UnicornException)],
    responses={404: {"description": "Something not found"}}
)


@brouter.get("/{items_id}")
async def get_spec_user(item_id: int):
    return {"Blitz": "The O is silent"}


'''You know what to do to achieve this in main.py '''
'''
app.include_router(users.router)
app.include_router(items.router)
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_token_header)],
    responses={418: {"description": "I'm a teapot"}},
)

'''
