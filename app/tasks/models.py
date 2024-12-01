import sqlalchemy as sa
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP

from config import get_settings
from database import Base
from tasks.enums import TaskStatus, TaskType

settings = get_settings()


class Tasks(Base):
    __tablename__ = "tasks"
    id = sa.Column(sa.Integer, nullable=False, primary_key=True, index=True)
    status = sa.Column(
        sa.Enum(TaskStatus),
        nullable=False,
        default=TaskStatus.INITIATED,
        server_default=TaskStatus.INITIATED,
    )
    task_type = sa.Column(
        sa.Enum(TaskType),
        nullable=False,
        default=TaskType.TICKER_CREATOR,
        server_default=TaskType.TICKER_CREATOR,
    )
    run_date = sa.Column(sa.Date, nullable=True)
    depends_on = sa.Column(sa.Integer, ForeignKey("tasks.id"), nullable=True)
    created_at = sa.Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = sa.Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
        onupdate=func.current_timestamp(),
    )
