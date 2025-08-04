from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import AddTask
from app.crud import create_task, get_all_tasks, delete_task, get_pct_completion, get_tasks_by_user
from app.schema import CreateTask, CreateTaskOut
from app.auth.dependency import get_current_user
from datetime import date


router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/get-todos", response_class=HTMLResponse)
async def get_todos(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user)):
    tasks = await get_tasks_by_user(db=db, current_user=user)
    return templates.TemplateResponse("mytodos.html", {"request": request, "tasks": tasks, "user": user})


@router.post("/update-task/{task_id}", response_class=RedirectResponse)
async def update_task_status(task_id: int, status: str = Form(...), db: Session=Depends(get_db)):
    task = db.query(AddTask).filter(AddTask.id == task_id).first()
    if task:
        task.status = status #type: ignore
        if status == "Completed":
            task.completion_date = date.today() #type: ignore
        else:
            task.completion_date = None #type: ignore
        db.commit()
    return RedirectResponse(url="/todos/get-todos", status_code=303)

@router.post("/delete-task/{task_id}", response_class=RedirectResponse)
async def delete_task_route(task_id: int, db: Session = Depends(get_db)):
    await delete_task(db=db, task_id=task_id)
    return RedirectResponse(url="/todos/get-todos", status_code=303)