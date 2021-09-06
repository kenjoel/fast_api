from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

client = TestClient(app)


@app.get("/")
async def read():
    return {"Hello": "World"}


def test_read():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}
