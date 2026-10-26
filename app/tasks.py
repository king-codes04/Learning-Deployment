import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field, field_validator

from app.database import get_db

router = APIRouter(prefix="/api/tasks", tags=["tasks"])
Database = Annotated[sqlite3.Connection, Depends(get_db)]


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Title must not be blank")
        return value


class TaskUpdate(BaseModel):
    completed: bool


class TaskRead(BaseModel):
    id: int
    title: str
    completed: bool


def task_from_row(row: sqlite3.Row) -> TaskRead:
    return TaskRead(
        id=row["id"],
        title=row["title"],
        completed=bool(row["completed"]),
    )


@router.get("", response_model=list[TaskRead])
def list_tasks(connection: Database) -> list[TaskRead]:
    rows = connection.execute(
        "SELECT id, title, completed FROM tasks ORDER BY id"
    ).fetchall()
    return [task_from_row(row) for row in rows]


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, connection: Database) -> TaskRead:
    cursor = connection.execute(
        "INSERT INTO tasks (title) VALUES (?)",
        (task.title,),
    )
    connection.commit()
    row = connection.execute(
        "SELECT id, title, completed FROM tasks WHERE id = ?",
        (cursor.lastrowid,),
    ).fetchone()
    return task_from_row(row)


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    task: TaskUpdate,
    connection: Database,
) -> TaskRead:
    cursor = connection.execute(
        "UPDATE tasks SET completed = ? WHERE id = ?",
        (int(task.completed), task_id),
    )
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    connection.commit()
    row = connection.execute(
        "SELECT id, title, completed FROM tasks WHERE id = ?",
        (task_id,),
    ).fetchone()
    return task_from_row(row)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, connection: Database) -> Response:
    cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    connection.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
