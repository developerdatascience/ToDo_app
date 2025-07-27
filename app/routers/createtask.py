from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import create_task, get_all_tasks, delete_task, get_pct_completion
from app.schema import CreateTask, CreateTaskOut
from datetime import date


router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("landingpage.html", {"request": request})

@router.get("/add-todos", response_class=HTMLResponse)
async def goto_todos(request: Request, db: Session = Depends(get_db)):
    tasks = await get_all_tasks(db=db)
    pct_completion = await get_pct_completion(db=db)
    return templates.TemplateResponse("base.html", {"request": request, "tasks": tasks, "pct_completion": int(pct_completion)})


@router.post("/add-task", response_model=CreateTaskOut)
async def add_task(request: Request, 
                   title: str = Form(...),
                   description: str = Form(None),
                   priority: str = Form(...),
                   calendar: str = Form(None),
                   db: Session = Depends(get_db)):
    
    # Convert the calendar string to date object
    due_date = date.fromisoformat(calendar) if calendar else None
    task_data = CreateTask(
        title=title,
        description=description,
        priority=priority,
        due_date=due_date)

    db_task = await create_task(db=db, task=task_data)
    return RedirectResponse(url="/tasks/add-todos", status_code=303)


@router.post("/delete-task/{task_id}", response_class=RedirectResponse)
async def delete_task_route(task_id: int, db: Session = Depends(get_db)):
    await delete_task(db=db, task_id=task_id)
    return RedirectResponse(url="/tasks/add-todos", status_code=303)
