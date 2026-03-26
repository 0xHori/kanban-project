import asyncio
from pathlib import Path

import aiosqlite

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "Database.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"

FIXED_TEST_TASKS = [
    {
        "task_name": "Задание 1 (Открытое)",
        "task_description": "Сверстать тестовую страницу",
        "status": "open",
        "position": 100,
    },
    {
        "task_name": "Задание 2 (Запланированное)",
        "task_description": None,
        "status": "todo",
        "position": 100,
    },
    {
        "task_name": "Задание 3 (В процессе)",
        "task_description": "Подключить uvicorn",
        "status": "in_progress",
        "position": 100,
    },
    {
        "task_name": "Задание 4 (Выполненное)",
        "task_description": "Подключить базу данных",
        "status": "done",
        "position": 100,
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
    position: int,
    task_description: str | None = None,
) -> int:
    async with conn.execute(
        """
        INSERT INTO tasks (task_name, task_description, status, position)
        VALUES (?, ?, ?, ?)
        """,
        (task_name, task_description, status, position),
    ) as cursor:
        await conn.commit()
        return cursor.lastrowid


async def seed_tasks(conn: aiosqlite.Connection) -> None:
    for task in FIXED_TEST_TASKS:
        await create_task(
            conn=conn,
            task_name=task["task_name"],
            status=task["status"],
            position=task["position"],
            task_description=task["task_description"],
        )


async def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("PRAGMA foreign_keys = ON;")
        await load_schema(conn, SCHEMA_PATH)
        await seed_tasks(conn)

    print("База создана и заполнена тестовыми задачами.")


if __name__ == "__main__":
    asyncio.run(main())