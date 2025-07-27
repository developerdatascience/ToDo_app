from datetime import date
from pydantic import BaseModel, field_validator

class CreateTaskBase(BaseModel):
    title: str
    description: str | None = None
    due_date: date | None = None
    priority: str | None = None

    @field_validator('due_date', mode='before')
    def parse_due_date(cls, value):
        if isinstance(value, str):
            return date.fromisoformat(value)
        return value

class CreateTask(CreateTaskBase):
    pass

class CreateTaskOut(CreateTaskBase):
    id: int
    status: str = "Pending"

    class Config:
        orm_mode = True

class UpdateTaskSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: date | None = None
    priority: str | None = None
    status: str | None = "Pending"
    completion_date: date | None = None

    @field_validator('due_date', 'completion_date', mode='before')
    def parse_dates(cls, value):
        if isinstance(value, str):
            return date.fromisoformat(value)
        return value

    class Config:
        orm_mode = True
