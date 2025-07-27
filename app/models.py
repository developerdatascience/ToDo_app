from sqlalchemy import Column, Integer, String, DateTime, Date, event
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime, date


class AddTask(Base):
    """Represents a task with due date and status"""
    __tablename__ = "addTask"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    priority = Column(String, nullable=False)
    due_date = Column(Date, default=date.today)
    days_remaining = Column(Integer, nullable=True)
    status = Column(String, default="Pending")
    completion_date = Column(Date, nullable=True)
    modified_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

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
