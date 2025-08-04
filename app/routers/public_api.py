from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import create_task, get_all_tasks
from app.schema import CreateTask, CreateTaskOut
from datetime import date
from typing import Optional

router = APIRouter(prefix="/api", tags=["public-api"])

# GET all tasks (public)
@router.get("/tasks", response_model=list[CreateTaskOut])
async def api_get_tasks(db: Session = Depends(get_db)):
    tasks = await get_all_tasks(db=db)
    return tasks

# POST create a new task (public)
@router.post("/tasks", response_model=CreateTaskOut)
async def api_create_task(
    title: str,
    description: Optional[str] = None,
    priority: str = "Normal",
    repeat: str = "None",
    due_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    due_date_obj = date.fromisoformat(due_date) if due_date else None
    task_data = CreateTask(
        title=title,
        description=description,
        priority=priority,
        repeat=repeat,
        due_date=due_date_obj
    )
    db_task = await create_task(db=db, task=task_data)
    return db_task
