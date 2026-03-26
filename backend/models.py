from typing import Optional

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    task_name: str
    task_description: Optional[str] = None


class TaskRead(BaseModel):
    id: int
    task_name: str
    task_description: Optional[str] = None
    status: str = Field(..., pattern=r"^(open|todo|in_progress|done)$")
    position: int
    created_at: str
    updated_at: str


class TaskUpdate(BaseModel):
    task_name: Optional[str] = None
    task_description: Optional[str] = None
    status: Optional[str] = Field(None, pattern=r"^(open|todo|in_progress|done)$")
    position: Optional[int] = None


class TaskMove(BaseModel):
    status: str = Field(..., pattern=r"^(open|todo|in_progress|done)$")
    position: int