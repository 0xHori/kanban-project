from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import aiosqlite


app = FastAPI()
DATABASE_FILE = "Database.db"


class TaskCreate(BaseModel):
    task_name: str
    task_description: Optional[str] = None


class TaskRead(BaseModel):
    id: int
    task_name: str
    task_description: Optional[str] = None
    status: str = Field(..., pattern=r"^(open|todo|in_progress|done)$")


async def get_tasks_from_db() -> list[TaskRead]:
    async with aiosqlite.connect(DATABASE_FILE) as con:
        cur = await con.execute(
            "SELECT id, task_name, task_description, status FROM tasks"
        )
        rows = await cur.fetchall()

        return [
            TaskRead(
                id=row[0],
                task_name=row[1],
                task_description=row[2],
                status=row[3],
            )
            for row in rows
        ]

async def get_task_from_db(task_id: int) -> TaskRead:
    async with aiosqlite.connect(DATABASE_FILE) as con:
        cur = await con.execute(
            "SELECT id, task_name, task_description, status FROM tasks WHERE id = ?",
            (task_id,)
        )
        row = await cur.fetchall()

        if row is None:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        
        return TaskRead(
            id=row[0],
            task_name=row[1],
            task_description=row[2],
            status=row[3],
        )


async def create_task(task_data: TaskCreate) -> dict:
    async with aiosqlite.connect(DATABASE_FILE) as con:
        try:
            cur = await con.execute(
                """
                INSERT INTO tasks (task_name, task_description, status)
                VALUES (?, ?, ?)
                """,
                (task_data.task_name, task_data.task_description, "open"),
            )
            await con.commit()

            return {
                "id": cur.lastrowid,
                "message": "Задача создана",
            }

        except aiosqlite.IntegrityError as err:
            raise HTTPException(
                status_code=400,
                detail=f"Ошибка целостности БД: {err}"
            )



@app.get("/")
async def read_root():
    return {"hello": "World"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/tasks", response_model=list[TaskRead])
async def get_tasks():
    return await get_tasks_from_db()


@app.post("/tasks", status_code=201)
async def post_task(task: TaskCreate):
    return await create_task(task)


@app.get("/tasks/{task_id}", response_model=TaskRead)
async def get_task(task_id: int):
    return await get_task_from_db(task_id)


