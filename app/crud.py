from sqlalchemy.orm import Session
from app.models.models import AddTask, User
from app.schema import CreateTask, UpdateTaskSchema
from datetime import date


async def create_task(db: Session, task: CreateTask, current_user: User):
    task_data = task.model_dump(exclude_unset=True)
    task_data["user_id"] = current_user.id

    # ensure due_date is a date object
    # if task_data.get("due_date") and isinstance(task_data["due_date"], str):
    #     task_data["due_date"] = date.fromisoformat(task_data["due_date"])

    db_task = AddTask(**task_data)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_task_by_id(db: Session, task_id: int):
    return db.query(AddTask).filter(AddTask.id == task_id).first()

async def get_tasks_by_user_top_5(db: Session, current_user: User):
    return db.query(AddTask).filter(AddTask.user_id == current_user.id).order_by(AddTask.created_at.desc()).limit(5)

async def get_tasks_by_user(db: Session, current_user: User):
    return db.query(AddTask).filter(AddTask.user_id == current_user.id).all()

async def get_all_tasks(db: Session):
    return db.query(AddTask).all()

async def delete_task(db: Session, task_id: int):
    db_task = db.query(AddTask).filter(AddTask.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
    

async def update_task(db: Session, task_id: int, task: UpdateTaskSchema):
    db_task = db.query(AddTask).filter(AddTask.id == task_id).first()
    if db_task:
        # Create a dictionary of all values including None
        update_values = task.model_dump()
        
        # Update only the fields that are present in the schema
        for field in update_values:
            setattr(db_task, field, update_values[field])
        
        db.commit()
        db.refresh(db_task)
        return db_task


async def get_pct_completion(db: Session, current_user: User):
    total_tasks = db.query(AddTask).filter(AddTask.user_id == current_user.id).count()
    completed_tasks = db.query(AddTask).filter(
        AddTask.user_id == current_user.id,
        AddTask.status == "Completed").count()
    
    if total_tasks == 0:
        return 0.0
    
    return (completed_tasks / total_tasks) * 100