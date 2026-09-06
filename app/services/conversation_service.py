import json
import os
import shutil
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path


def _app_data_dir() -> Path:
    override = os.getenv("NEXAMIND_DATA_DIR")
    if override:
        root = Path(override).expanduser()
    elif os.name == "nt":
        root = Path(os.getenv("LOCALAPPDATA", Path.home())) / "NexaMind"
    elif os.uname().sysname == "Darwin":
        root = Path.home() / "Library" / "Application Support" / "NexaMind"
    else:
        root = Path.home() / ".local" / "share" / "NexaMind"
    root.mkdir(parents=True, exist_ok=True)
    return root


APP_DATA_DIR = _app_data_dir()
DB_PATH = APP_DATA_DIR / "nexamind.db"
WORKSPACES_DIR = APP_DATA_DIR / "workspaces"
WORKSPACES_DIR.mkdir(parents=True, exist_ok=True)


def _connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _now():
    return datetime.now(timezone.utc).isoformat()


def initialize_database():
    with _connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                dataset_id TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS workbooks (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                local_path TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                payload_json TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            );
            """
        )


def create_conversation(dataset_id: str | None = None, title: str = "New analysis"):
    initialize_database()
    conversation_id = str(uuid.uuid4())
    dataset_id = dataset_id or str(uuid.uuid4())
    now = _now()
    with _connect() as db:
        db.execute(
            "INSERT INTO conversations(id, title, dataset_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (conversation_id, title, dataset_id, now, now),
        )
    return get_conversation(conversation_id)


def get_conversation(conversation_id: str):
    initialize_database()
    with _connect() as db:
        row = db.execute("SELECT * FROM conversations WHERE id = ?", (conversation_id,)).fetchone()
        return dict(row) if row else None


def get_conversation_by_dataset(dataset_id: str):
    initialize_database()
    with _connect() as db:
        row = db.execute("SELECT * FROM conversations WHERE dataset_id = ?", (dataset_id,)).fetchone()
        return dict(row) if row else None


def list_conversations():
    initialize_database()
    with _connect() as db:
        rows = db.execute(
            """
            SELECT c.*, COUNT(DISTINCT w.id) AS file_count
            FROM conversations c
            LEFT JOIN workbooks w ON w.conversation_id = c.id
            GROUP BY c.id
            ORDER BY c.updated_at DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]


def update_title(conversation_id: str, title: str):
    title = title.strip() or "New analysis"
    with _connect() as db:
        db.execute(
            "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
            (title, _now(), conversation_id),
        )
    return get_conversation(conversation_id)


def touch_conversation(conversation_id: str):
    with _connect() as db:
        db.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (_now(), conversation_id))


def maybe_set_title_from_question(conversation_id: str, question: str):
    conversation = get_conversation(conversation_id)
    if not conversation or conversation["title"] != "New analysis":
        return
    clean = " ".join(question.strip().split())
    title = clean if len(clean) <= 42 else clean[:39].rstrip() + "..."
    update_title(conversation_id, title or "New analysis")


def workspace_dir(conversation_id: str):
    path = WORKSPACES_DIR / conversation_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def replace_workbooks(conversation_id: str, uploaded_files: list[tuple[str, bytes]]):
    target = workspace_dir(conversation_id)
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True, exist_ok=True)
    with _connect() as db:
        db.execute("DELETE FROM workbooks WHERE conversation_id = ?", (conversation_id,))
        for filename, content in uploaded_files:
            workbook_id = str(uuid.uuid4())
            safe_name = Path(filename).name
            local_path = target / f"{workbook_id}__{safe_name}"
            local_path.write_bytes(content)
            db.execute(
                "INSERT INTO workbooks(id, conversation_id, filename, local_path, created_at) VALUES (?, ?, ?, ?, ?)",
                (workbook_id, conversation_id, safe_name, str(local_path), _now()),
            )
    touch_conversation(conversation_id)


def add_workbooks(conversation_id: str, uploaded_files: list[tuple[str, bytes]]):
    target = workspace_dir(conversation_id)
    with _connect() as db:
        for filename, content in uploaded_files:
            workbook_id = str(uuid.uuid4())
            safe_name = Path(filename).name
            local_path = target / f"{workbook_id}__{safe_name}"
            local_path.write_bytes(content)
            db.execute(
                "INSERT INTO workbooks(id, conversation_id, filename, local_path, created_at) VALUES (?, ?, ?, ?, ?)",
                (workbook_id, conversation_id, safe_name, str(local_path), _now()),
            )
    touch_conversation(conversation_id)


def list_workbook_records(conversation_id: str):
    with _connect() as db:
        rows = db.execute(
            "SELECT * FROM workbooks WHERE conversation_id = ? ORDER BY created_at",
            (conversation_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def delete_workbook(conversation_id: str, workbook_id: str):
    with _connect() as db:
        row = db.execute(
            "SELECT local_path FROM workbooks WHERE id = ? AND conversation_id = ?",
            (workbook_id, conversation_id),
        ).fetchone()
        if not row:
            return False
        Path(row["local_path"]).unlink(missing_ok=True)
        db.execute("DELETE FROM workbooks WHERE id = ?", (workbook_id,))
    touch_conversation(conversation_id)
    return True


def save_exchange(conversation_id: str, question: str, response_payload: dict):
    now = _now()
    with _connect() as db:
        db.execute(
            "INSERT INTO messages(id, conversation_id, role, content, payload_json, created_at) VALUES (?, ?, 'user', ?, NULL, ?)",
            (str(uuid.uuid4()), conversation_id, question, now),
        )
        db.execute(
            "INSERT INTO messages(id, conversation_id, role, content, payload_json, created_at) VALUES (?, ?, 'assistant', ?, ?, ?)",
            (
                str(uuid.uuid4()),
                conversation_id,
                response_payload.get("answer", ""),
                json.dumps(response_payload, default=str),
                _now(),
            ),
        )
    maybe_set_title_from_question(conversation_id, question)
    touch_conversation(conversation_id)


def list_messages(conversation_id: str):
    with _connect() as db:
        rows = db.execute(
            "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at, rowid",
            (conversation_id,),
        ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["payload"] = json.loads(item["payload_json"]) if item["payload_json"] else None
        item.pop("payload_json", None)
        result.append(item)
    return result


def delete_conversation(conversation_id: str):
    conversation = get_conversation(conversation_id)
    if not conversation:
        return False
    with _connect() as db:
        db.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
    shutil.rmtree(WORKSPACES_DIR / conversation_id, ignore_errors=True)
    return True
