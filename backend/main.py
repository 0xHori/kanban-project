from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

from backend.crud import (
    create_task,
    delete_task_from_db,
    get_task_from_db,
    get_tasks_from_db,
    move_task_from_db,
    patch_task_from_db,
)
from backend.models import TaskCreate, TaskMove, TaskRead, TaskUpdate


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"service": "kanban-api"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/tasks", response_model=list[TaskRead])
async def get_tasks():
    return await get_tasks_from_db()


@app.post("/tasks", response_model=TaskRead, status_code=201)
async def post_task(task: TaskCreate):
    return await create_task(task)


@app.get("/tasks/{task_id}", response_model=TaskRead)
async def get_task(task_id: int):
    return await get_task_from_db(task_id)


@app.patch("/tasks/{task_id}", response_model=TaskRead)
async def patch_task(task_id: int, task: TaskUpdate):
    return await patch_task_from_db(task_id, task)


@app.patch("/tasks/{task_id}/move", response_model=TaskRead)
async def move_task(task_id: int, move_data: TaskMove):
    return await move_task_from_db(task_id, move_data)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int):
    await delete_task_from_db(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)