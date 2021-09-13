from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="../static"), name="static")

templates = Jinja2Templates(directory="../templates")


@app.get("/temp", response_class=HTMLResponse)
def get_temp(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request":request, "id":id})

