from typing import Optional

from couchbase_core._libcouchbase import LOCKMODE_WAIT
from couchbase.bucket import Bucket
from couchbase.cluster import Cluster, PasswordAuthenticator
from fastapi import FastAPI
from pydantic import BaseModel

USER_PROFILE_DOC_TYPE = "userprofile"


def getBucket():
    cluster = Cluster(
        "couchbase://couchbasehost:8091?fetch_mutation_tokens=1&operation_timeout=30&n1ql_timeout=300"
    )
    authenticator = PasswordAuthenticator("username", "password")
    cluster.authenticate(authenticator)
    bucket: Bucket = cluster.open_bucket("bucket_name", lockmode=LOCKMODE_WAIT)
    bucket.timeout = 30
    bucket.n1ql_timeout = 300
    return bucket


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    type: str = USER_PROFILE_DOC_TYPE
    hashed_password: str


def get_user(bucket: Bucket, username: str):
    doc_id = f"userprofile::{username}"
    result = bucket.get(doc_id, quiet=True)
    if not result.value:
        return None
    user = UserInDB(**result.value)
    return user


app = FastAPI()


@app.get("/users/{username}", response_model=User)
def read_user(username: str):
    bucket = getBucket()
    user = get_user(bucket=bucket, username=username)
    return user