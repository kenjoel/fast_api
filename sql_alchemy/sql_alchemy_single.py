from typing import List

import databases
import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

DB_Location = "sqlite:///./my_sqlite.db"

# engine = create_engine(DB_Location, {"check_same_thread": False})
#
# session_initializer = sessionmaker(autoflush=False, autocommit=False, bind=engine)
#
# Base = declarative_base()
#
# Base.metadata.createall(bind=engine)

database = databases.Database(DB_Location)

metadata = sqlalchemy.MetaData()

notes = sqlalchemy.Table(
    "notes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("text", sqlalchemy.String),
    sqlalchemy.Column("completed", sqlalchemy.Boolean)
)

engine = sqlalchemy.create_engine(DB_Location, connect_args={"check_same_thread": False})

metadata.create_all(bind=engine)


class NoteIn(BaseModel):
    text: str
    completed: bool


class Note(BaseModel):
    id: int
    text: str
    completed: bool


@app.on_event("startup")
async def start_connection():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/notes", response_model=List[Note])
async def get_notes():
    query = database.fetch_all(notes.select())
    return await query


@app.post("/notes", response_model=Note)
async def post_notes(note: NoteIn):
    query = notes.insert().values(text=note.text, completed=note.completed)
    record_id = await database.execute(query)
    return {**note.dict(), "id": record_id}
