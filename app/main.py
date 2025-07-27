from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import createtask
from app.routers import todotable

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="To-Do List API")
app.mount("/static", StaticFiles(directory="static"), name="static")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=createtask.router, prefix="/tasks", tags=["tasks"])
app.include_router(router=todotable.router, prefix="/todos", tags=["todos"])



