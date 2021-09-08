from fastapi import FastAPI
from starlette.responses import HTMLResponse, RedirectResponse, StreamingResponse, FileResponse, JSONResponse, Response

app = FastAPI()


@app.get("/slide", response_class=HTMLResponse)
async def get_html():
    return """
    <html>
    <h1>Look ma! HTML </div>
    <div> hello world</div>
    <div> I'm coming to visit you </div>
    </html>
           """


"THE SAME EXAMPLE COULD LOOK LIKE THIS"


@app.get("/alternative")
async def get_alternative():
    html_content = """
     <html>
    <h1>Look ma! HTML </div>
    <div> hello world</div>
    <div> I'm coming to visit you </div>
    </html>
    """

    return HTMLResponse(html_content, status_code=200)


'''REDIRECT '''


@app.get("/redirect")
async def redirect_me():
    return RedirectResponse("http://youtube.com")


async def fake_video_streamer():
    for i in range(10):
        yield b"some fake video bytes"


@app.get("/")
async def main():
    return StreamingResponse(fake_video_streamer())


'''We can create a generator to iterate over a file like object 
so that we don't have to read it all first from Memory'''

file = "someFilePath.mp4"


def generator_for_file():
    with open(file, mode="rb") as file_object:
        yield from file_object


@app.get("/video")
async def get_video():
    return StreamingResponse(generator_for_file, status_code=200, media_type="video/mp4")


'''oor we could just use file response like so which allows asynchronicity'''


@app.get("/alternative_video")
async def asynchronicity():
    return FileResponse(file, media_type="video/ovi", status_code=200)


'''You can set cookies as well'''


@app.post("/cookie/")
def create_cookie():
    content = {"message": "Come to the dark side, we have cookies"}
    response = JSONResponse(content=content)
    response.set_cookie(key="fakesession", value="fake-cookie-session-value")
    return response


"""You Can set Temporal headers too"""
'''Have in mind that custom proprietary headers can be added using the 'X-' prefix.'''


@app.get("/headers-and-object/")
def get_headers(response: Response):
    response.headers["X-Cat-Dog"] = "alone in the world"
    return {"message": "Hello World"}
