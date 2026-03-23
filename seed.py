import asyncio
from pathlib import Path

import aiosqlite

DB_PATH = Path("Database.db")
SCHEMA_PATH = Path("schema.sql")

FIXED_TEST_TASKS = [
    {
        "task_name": "Задание 1 (Открытое)",
        "task_description": "Сверстать тестовую страницу",
        "status": "open",
    },
    {
        "task_name": "Задание 2 (Запланированное)",
        "task_description": None,
        "status": "todo",
    },
    {
        "task_name": "Задание 3 (В процессе)",
        "task_description": "Подключить uvicorn",
        "status": "in_progress",
    },
    {
        "task_name": "Задание 4 (Выполненное)",
        "task_description": "Подключить базу данных",
        "status": "done",
    },
]


async def load_schema(conn: aiosqlite.Connection, schema_path: Path) -> None:
    schema_sql = schema_path.read_text(encoding="utf-8")
    await conn.executescript(schema_sql)
    await conn.commit()


async def create_task(
    conn: aiosqlite.Connection,
    task_name: str,
    status: str,
    task_description: str | None = None,
) -> int:
    async with conn.execute(
        """
        INSERT INTO tasks (task_name, task_description, status)
        VALUES (?, ?, ?)
        """,
        (task_name, task_description, status),
    ) as cursor:
        await conn.commit()
        return cursor.lastrowid


async def seed_tasks(conn: aiosqlite.Connection) -> None:
    for task in FIXED_TEST_TASKS:
        await create_task(
            conn=conn,
            task_name=task["task_name"],
            status=task["status"],
            task_description=task["task_description"],
        )


async def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("PRAGMA foreign_keys = ON;")
        await load_schema(conn, SCHEMA_PATH)
        await seed_tasks(conn)

    print("База создана и заполнена 4 тестовыми задачами.")


if __name__ == "__main__":
    asyncio.run(main())