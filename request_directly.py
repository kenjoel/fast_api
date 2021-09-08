from fastapi import FastAPI
from starlette.requests import Request

app = FastAPI()


@app.get("/client_ip/{item_id}")
def get_client_ip(item_id: str, request: Request):
    client_ip = request.client.host
    return {"client_host": client_ip, "Westlife": item_id}


