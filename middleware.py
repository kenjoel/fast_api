import time

from fastapi import FastAPI, Request
from fastapi.openapi.models import Response
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from sql_alchemy.database import SessionLocal

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

'''WE CAN CREATE A MIDDLEWARE THAT INITIALIZES A DB SESSION'''


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
        print(response)
    return response


# Dependency
def get_db(request: Request):
    return request.state.db


'''ENDS HERE '''

'''HTTPSREDIRECT MIDDLEWARE '''

# Enforces that all incoming requests must either be https or ws
# and will be redirected to secure scheme

app.add_middleware(HTTPSRedirectMiddleware)


@app.get("/https_wss")
def enforce_security():
    return


'''TRUSTEDHOSTMIDDLEWARE'''
# Enforces that all incoming requests have a correctly set Host header, in order to guard against HTTP Host Header
# attacks.

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["nyamnyam.com", "bumbum.com", "*.example.com"])

'''GZipMiddleware'''
# GZip responses for any request that includes "gzip" in the Accept-Encoding header.
app.add_middleware(GZipMiddleware, minimum_size=100)
