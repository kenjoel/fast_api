from fastapi import FastAPI

app = FastAPI()


@app.get("/app")
def read_main():
    return {"message": "Hello World from main app"}


subapi = FastAPI()


@subapi.get("/sub")
def get_suby():
    return {"Good morning": "USA"}


app.mount("/subapi", subapi)
