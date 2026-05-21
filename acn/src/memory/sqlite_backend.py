# src/memory/sqlite_backend.py
"""
SQLite Persistence Backend for MultiModalMemory.

Every memory trace written to ACN survives process restarts.
Zero external dependencies — uses Python stdlib sqlite3.

Principle: A fleet with amnesia is a fleet that never learns.

Inspired by:
- PicoClaw's append-only JSONL philosophy (never destroy the past)
- Strands AI Functions persistent memory backends
- SQLite's "zero-config, works everywhere" design

[CITATION: PicoClaw2026]
[CITATION: Strands2026]
"""

import json
import sqlite3
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

from shared.utils.citations import cite
from memory.architecture import MemoryType, MemoryTrace


@cite(
    key="SQLITE-MEMORY",
    paper="SQLite Persistence for Cognitive Memory",
    venue="ACN Memory Architecture",
    section="Persistent Backends",
    rationale="Zero-dependency persistence using stdlib sqlite3",
    confidence="HIGH",
)
class SQLiteMemoryBackend:
    """
    SQLite-backed persistence for memory traces.

    Usage:
        backend = SQLiteMemoryBackend("acn_memory.db")
        backend.store(trace)
        traces = backend.retrieve(memory_type=MemoryType.EPISODIC, limit=10)
    """

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._ensure_schema()

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _ensure_schema(self) -> None:
        conn = self._get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory_traces (
                trace_id TEXT PRIMARY KEY,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp REAL NOT NULL,
                source TEXT,
                confidence REAL NOT NULL DEFAULT 1.0,
                importance REAL NOT NULL DEFAULT 0.5,
                tags TEXT NOT NULL DEFAULT '[]',
                causal_links TEXT NOT NULL DEFAULT '[]',
                access_count INTEGER NOT NULL DEFAULT 0,
                last_accessed REAL NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_memory_type ON memory_traces(memory_type)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON memory_traces(timestamp)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_source ON memory_traces(source)
        """)
        conn.commit()

    def store(self, trace: MemoryTrace) -> None:
        """Persist a memory trace."""
        conn = self._get_conn()
        conn.execute(
            """
            INSERT OR REPLACE INTO memory_traces
            (trace_id, memory_type, content, timestamp, source, confidence,
             importance, tags, causal_links, access_count, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                trace.trace_id,
                trace.memory_type.value,
                json.dumps(trace.content) if not isinstance(trace.content, str) else trace.content,
                trace.timestamp,
                trace.source,
                trace.confidence,
                trace.importance,
                json.dumps(trace.tags),
                json.dumps(trace.causal_links),
                trace.access_count,
                trace.last_accessed,
            ),
        )
        conn.commit()

    def retrieve(
        self,
        memory_type: Optional[MemoryType] = None,
        source: Optional[str] = None,
        tag: Optional[str] = None,
        limit: int = 100,
        order_by: str = "timestamp DESC",
    ) -> List[MemoryTrace]:
        """Retrieve traces with optional filtering."""
        conn = self._get_conn()
        conditions: List[str] = []
        params: List[Any] = []

        if memory_type is not None:
            conditions.append("memory_type = ?")
            params.append(memory_type.value)
        if source is not None:
            conditions.append("source = ?")
            params.append(source)
        if tag is not None:
            conditions.append("tags LIKE ?")
            params.append(f'%"{tag}"%')

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        query = f"SELECT * FROM memory_traces {where_clause} ORDER BY {order_by} LIMIT ?"
        params.append(limit)

        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        return [self._row_to_trace(row) for row in rows]

    def get_by_id(self, trace_id: str) -> Optional[MemoryTrace]:
        """Retrieve a single trace by ID."""
        conn = self._get_conn()
        row = conn.execute(
            "SELECT * FROM memory_traces WHERE trace_id = ?", (trace_id,)
        ).fetchone()
        return self._row_to_trace(row) if row else None

    def delete(self, trace_id: str) -> bool:
        """Delete a trace. Returns True if found."""
        conn = self._get_conn()
        cursor = conn.execute("DELETE FROM memory_traces WHERE trace_id = ?", (trace_id,))
        conn.commit()
        return cursor.rowcount > 0

    def count(self, memory_type: Optional[MemoryType] = None) -> int:
        """Count traces, optionally filtered by type."""
        conn = self._get_conn()
        if memory_type:
            row = conn.execute(
                "SELECT COUNT(*) FROM memory_traces WHERE memory_type = ?",
                (memory_type.value,),
            ).fetchone()
        else:
            row = conn.execute("SELECT COUNT(*) FROM memory_traces").fetchone()
        return row[0] if row else 0

    def load_all(self) -> Dict[MemoryType, List[MemoryTrace]]:
        """Load all traces grouped by memory type."""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM memory_traces ORDER BY timestamp")
        result: Dict[MemoryType, List[MemoryTrace]] = {
            mt: [] for mt in MemoryType
        }
        for row in cursor.fetchall():
            trace = self._row_to_trace(row)
            result[trace.memory_type].append(trace)
        return result

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def _row_to_trace(self, row: sqlite3.Row) -> MemoryTrace:
        content = row["content"]
        try:
            content = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            pass  # Keep as string if not valid JSON

        return MemoryTrace(
            trace_id=row["trace_id"],
            memory_type=MemoryType(row["memory_type"]),
            content=content,
            timestamp=row["timestamp"],
            source=row["source"],
            confidence=row["confidence"],
            importance=row["importance"],
            tags=json.loads(row["tags"]),
            causal_links=json.loads(row["causal_links"]),
            access_count=row["access_count"],
            last_accessed=row["last_accessed"],
        )
