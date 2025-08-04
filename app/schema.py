from datetime import date
from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional
from uuid import UUID

class CreateTaskBase(BaseModel):
    title: str
    description: str | None = None
    due_date: date | None = None
    priority: str | None = None
    repeat: str | None = None
    user_id: UUID

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
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    priority: Optional[str] = None
    repeat: Optional[str] = None
    status: Optional[str] = None

    @field_validator('due_date', mode='after')
    def parse_dates(cls, value):
        if isinstance(value, str):
            return date.fromisoformat(value)
        return value

    class Config:
        orm_mode = True


class RegisterUserRequest(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: str | None = None

    def get_uuid(self) -> UUID | None:
        if self.user_id:
            return UUID(self.user_id)
        return None
    
class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    hashed_password: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    new_password_confirm: str