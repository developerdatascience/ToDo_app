from sqlalchemy.orm import Session
from app.models import AddTask
from app.schema import CreateTask, UpdateTaskSchema
from datetime import date


async def create_task(db: Session, task: CreateTask):
    task_data = task.model_dump(exclude_unset=True)

    # ensure due_date is a date object
    # if task_data.get("due_date") and isinstance(task_data["due_date"], str):
    #     task_data["due_date"] = date.fromisoformat(task_data["due_date"])

    db_task = AddTask(**task_data)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

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
        for key, value in task.model_dump(exclude_unset=True).items():
            setattr(db_task, key, value)
        db.commit()
        db.refresh(db_task)
        return db_task
    return None


async def get_pct_completion(db: Session):
    total_tasks = db.query(AddTask).count()
    completed_tasks = db.query(AddTask).filter(AddTask.status == "Completed").count()
    print("total_tasks:", total_tasks)
    
    if total_tasks == 0:
        return 0.0
    
    return (completed_tasks / total_tasks) * 100
