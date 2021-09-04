import time

from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

'''
Have in mind that custom proprietary headers can be added using the 'X-' prefix.

But if you have custom headers that you want a client in a browser to be able to see, you need to add them to your 
CORS configurations (CORS (Cross-Origin Resource Sharing)) using the parameter expose_headers documented in 
Starlette's CORS docs. 
'''


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    return response


'''CORS MIDDLEWARE '''

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

'''ENDS HERE'''
