from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User
from app.auth.dependency import get_current_user
from app.crud import create_task, get_all_tasks, delete_task, get_pct_completion, update_task, get_task_by_id, get_tasks_by_user, get_tasks_by_user_top_5
from app.schema import CreateTask, CreateTaskOut, UpdateTaskSchema
from datetime import date


router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("base.html", {"request": request, "user": user})

@router.get("/add-todos", response_class=HTMLResponse)
async def goto_todos(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    tasks = await get_tasks_by_user_top_5(db=db, current_user=user)
    pct_completion = await get_pct_completion(db=db, current_user=user)
    return templates.TemplateResponse("addtask.html", {"request": request, "tasks": tasks, "pct_completion": int(pct_completion), "user": user})


@router.post("/add-task", response_model=CreateTaskOut)
async def add_task(request: Request, 
                   title: str = Form(...),
                   description: str = Form(None),
                   priority: str = Form(...),
                   repeat: str = Form(...),
                   calendar: str = Form(None),
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    
    # Convert the calendar string to date object
    due_date = date.fromisoformat(calendar) if calendar else None
    task_data = CreateTask(
        title=title,
        description=description,
        priority=priority,
        repeat=repeat,
        due_date=due_date,
        user_id=current_user.id)  #type: ignore

    db_task = await create_task(db=db, task=task_data, current_user=current_user)
    return RedirectResponse(url="/tasks/add-todos", status_code=303)


@router.post("/delete-task/{task_id}", response_class=RedirectResponse)
async def delete_task_route(task_id: int, db: Session = Depends(get_db)):
    await delete_task(db=db, task_id=task_id)
    return RedirectResponse(url="/tasks/add-todos", status_code=303)

@router.get("/update-task/{task_id}", response_class=HTMLResponse)
async def get_task_for_update(task_id: int, request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    tasks = get_task_by_id(db=db, task_id=task_id)
    if not tasks:
        return templates.TemplateResponse("404.html", {"request": request, "user": user})
    return templates.TemplateResponse("edittaskform.html", {"request": request, "tasks": tasks, "user": user})



@router.post("/update-task/{task_id}", response_class=RedirectResponse)
async def update_task_route(
    task_id: int,
    title: str = Form(None),
    description: str = Form(None),
    due_date: str = Form(None),
    priority: str = Form(None),
    repeat: str = Form(None),
    db: Session = Depends(get_db)
):
    # Handle empty date string
    due_date_value = None
    if due_date and due_date.strip():
        try:
            due_date_value = date.fromisoformat(due_date)
        except ValueError:
            # Handle invalid date format
            print("Invalid date format for due_date:", due_date)

    task_data = UpdateTaskSchema(
        title=title,
        description=description,
        due_date=due_date_value,
        priority=priority,
        repeat=repeat
    )
    try:
        await update_task(db=db, task_id=task_id, task=task_data)
        return RedirectResponse(url=f"/tasks/update-task/{task_id}?alert=success", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/tasks/update-task/{task_id}?alert=failed", status_code=303)
    

# Test endpoint to set a test cookie
@router.get("/set-test-cookie")
async def set_test_cookie():
    response = RedirectResponse(url="/tasks")
    response.set_cookie(key="test_cookie", value="cookie_value", httponly=False, secure=False)
    return response