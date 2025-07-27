from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AddTask
from app.crud import create_task, get_all_tasks, delete_task, get_pct_completion
from app.schema import CreateTask, CreateTaskOut
from datetime import date


router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/get-todos", response_class=HTMLResponse)
async def get_todos(request: Request, db: Session = Depends(get_db)):
    tasks = await get_all_tasks(db=db)
    return templates.TemplateResponse("mytodos.html", {"request": request, "tasks": tasks})


@router.post("/update-task/{task_id}", response_class=RedirectResponse)
async def update_task_status(task_id: int, status: str = Form(...), db: Session=Depends(get_db)):
    task = db.query(AddTask).filter(AddTask.id == task_id).first()
    if task:
        task.status = status
        if status == "Completed":
            task.completion_date = date.today()
        else:
            task.completion_date = None
        db.commit()
    return RedirectResponse(url="/todos/get-todos", status_code=303)

@router.post("/delete-task/{task_id}", response_class=RedirectResponse)
async def delete_task_route(task_id: int, db: Session = Depends(get_db)):
    await delete_task(db=db, task_id=task_id)
    return RedirectResponse(url="/todos/get-todos", status_code=303)
