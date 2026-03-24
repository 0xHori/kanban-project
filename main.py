from fastapi import FastAPI, HTTPException, Response, status
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

class TaskUpdate(BaseModel):
    task_name: Optional[str] = None
    task_description: Optional[str] = None
    status: Optional[str] = Field(None, pattern=r"^(open|todo|in_progress|done)$")

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
        row = await cur.fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        
        return TaskRead(
            id=row[0],
            task_name=row[1],
            task_description=row[2],
            status=row[3],
        )


async def create_task(task_data: TaskCreate) -> TaskRead:
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

            return TaskRead(
                id=cur.lastrowid,
                task_name=task_data.task_name,
                task_description=task_data.task_description,
                status="open",
            )

        except aiosqlite.IntegrityError as err:
            raise HTTPException(
                status_code=400,
                detail=f"Ошибка целостности БД: {err}"
            )

async def patch_task_from_db(task_id: int, task: TaskUpdate) -> TaskRead:
    async with aiosqlite.connect(DATABASE_FILE) as con:
        cur = await con.execute(
            "SELECT id, task_name, task_description, status FROM tasks WHERE id = ?",
            (task_id,)
        )
        row = await cur.fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="Задача не найдена")

        current = TaskRead(
            id=row[0],
            task_name=row[1],
            task_description=row[2],
            status=row[3],
        )


        new_name = (
            task.task_name
            if task.task_name is not None
            else current.task_name
        )
        new_description = (
            task.task_description
            if task.task_description is not None
            else current.task_description
        )
        new_status = (
            task.status
            if task.status is not None
            else current.status
        )

        await con.execute(
            """
            UPDATE tasks
            SET task_name = ?, task_description = ?, status = ?
            WHERE id = ?
            """,
            (new_name, new_description, new_status, task_id,),
        )
        await con.commit()

        return TaskRead(
            id=task_id,
            task_name=new_name,
            task_description=new_description,
            status=new_status,
        )

async def delete_task_from_db(task_id: int) -> None:
    async with aiosqlite.connect(DATABASE_FILE) as con:
        cur = await con.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )
        await con.commit()

        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Задача не найдена")





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


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int):
    await delete_task_from_db(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)