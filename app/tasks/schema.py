from datetime import datetime

from pydantic import BaseModel

from tasks.enums import TaskStatus, TaskType


class TaskResponse(BaseModel):
    id: int
    status: TaskStatus
    task_type: TaskType
    run_date: datetime
    depends_on: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
