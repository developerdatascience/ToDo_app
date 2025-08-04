from sqlalchemy import Column, Integer, String, DateTime, Date, event, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, date
from sqlalchemy.dialects.postgresql import UUID
import uuid



class User(Base):
    """Represents a user in the system"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_name = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now())

    logs = relationship("UserLoginLog", back_populates="user")
    tasks = relationship("AddTask", back_populates="user")

class UserLoginLog(Base):
    __tablename__ = "user_login_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    login_time = Column(DateTime, default=datetime.now())
    logout_time = Column(DateTime)
    user = relationship("User", back_populates="logs")
    


class AddTask(Base):
    """Represents a task with due date and status"""
    __tablename__ = "addTask"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    priority = Column(String, nullable=False)
    repeat = Column(String, nullable=True, default="No")
    due_date = Column(Date, default=date.today)
    days_remaining = Column(Integer, nullable=True)
    status = Column(String, default="Pending")
    completion_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="tasks")

    def calculate_days_remaining(self):
        """Calculate the number of days remaining until the due date."""
        if self.due_date:   # type: ignore
            return (self.due_date - date.today()).days
        return None


# ✅ Add this below the class definition
@event.listens_for(AddTask, 'before_insert')
@event.listens_for(AddTask, 'before_update')
def update_days_remaining(mapper, connection, target):
    """Automatically calculate days_remaining before insert/update."""
    if target.due_date:
        target.days_remaining = (target.due_date - date.today()).days

@event.listens_for(AddTask, "before_insert")
@event.listens_for(AddTask, "before_update")
def mark_task_completed(mapper, connection, target):
    """Mark the task as completed and set the completion date."""
    if target.status == "Completed":
        target.completion_date = date.today()
    else:
        target.completion_date = None

@event.listens_for(AddTask, "before_insert")
@event.listens_for(AddTask, "before_update")
def set_status_automatically(mapper, connection, target):
    """Set the status of the task based on the due date."""
    if target.due_date and target.due_date < date.today() and target.status != "Completed":
        target.status = "Overdue"
    elif target.status == "Completed":
        target.completion_date = date.today()
    else:
        target.status = "Pending"