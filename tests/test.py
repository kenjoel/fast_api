from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.websockets import WebSocket

from sql_alchemy.database import Base
from sql_alchemy.main import get_db

app = FastAPI()

client = TestClient(app)

items = {}

'''
async def override_dependency(q: Optional[str] = None):
    return {"q": q, "skip": 5, "limit": 10}
app.dependency_overrides[common_parameters] = override_dependency
'''


@app.get("/")
async def read():
    return {"Hello": "World"}


def test_read():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


@app.websocket_route("/ws")
async def websocket(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"msg": "Hello WebSocket"})
    await websocket.close()


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}


def test_websocket():
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        assert data == {"msg": "Hello WebSocket"}


@app.on_event("startup")
async def startup_event():
    items["foo"] = {"name": "Fighters"}
    items["bar"] = {"name": "Tenders"}


@app.get("/items/{item_id}")
async def read_items(item_id: str):
    return items[item_id]


def test_read_items():
    response = client.get("/items/foo")
    assert response.status_code == 200
    assert response.json() == {"name": "Fighters"}


'''TEST A DATABASE'''

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def test_create_user():
    response = client.post(
        "/users/",
        json={"email": "deadpool@example.com", "password": "chimichangas4life"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "deadpool@example.com"
    assert "id" in data
    user_id = data["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "deadpool@example.com"
    assert data["id"] == user_id
