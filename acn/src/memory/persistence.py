# src/memory/persistence.py
"""
Cross-Session Persistence for the Periodic Temporal Knowledge Graph.

Provides JSONL-based persistence with no external dependencies.
Each graph is stored as a single JSONL file where each line is a snapshot.
On load, the latest snapshot is restored. Incremental append mode enables
session-to-session accumulation without rewriting the entire file.

Design inspired by:
- Mem0 (Chhikara2025): Separation of write cost (one-time) from read cost
- Collective Memory: Persistent knowledge graph for multi-agent collaboration
- Sibyl: Knowledge graph that compounds across sessions

[CITATION: Mem02025]
[CITATION: CollectiveMemory2026]
[CITATION: Sibyl2026]
"""

import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

from shared.utils.citations import cite
from memory.ptkg import PTKG


@cite(
    key="PTKG-PERSIST",
    paper="Periodic Temporal Knowledge Graph for Agent Memory",
    venue="ACN Architecture Document",
    section="Persistence Layer",
    rationale="JSONL append-only persistence provides durability without external database dependencies",
    confidence="CERTAIN",
)
class PTKGPersistence:
    """
    [CITATION: PTKG-PERSISTENCE] Persistence manager for PTKG graphs.
    
    Storage format: JSONL (one JSON object per line)
    - Each line is a complete graph snapshot
    - On save: append new snapshot to file
    - On load: read last line (latest snapshot)
    - Optional compaction: keep only latest N snapshots
    
    This design mirrors Mem0's separation of extraction (graph construction)
    from retrieval (graph loading), amortizing write cost across sessions.
    """

    def __init__(self, storage_dir: Optional[str] = None, max_snapshots: int = 10):
        """[CITATION: PTKG-PERSISTENCE] Initialize persistence manager."""
        self.storage_dir = Path(storage_dir) if storage_dir else Path(".ptkg_store")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.max_snapshots = max_snapshots

    def _graph_path(self, graph_id: str) -> Path:
        """[CITATION: PTKG-PERSISTENCE] Get the file path for a given graph ID."""
        return self.storage_dir / f"{graph_id}.jsonl"

    def save(self, graph: PTKG) -> Path:
        """
        [CITATION: PTKG-PERSISTENCE] Save a graph snapshot. Appends to existing JSONL file.
        Returns the path to the saved file.
        """
        path = self._graph_path(graph.graph_id)
        snapshot = graph.to_dict()
        snapshot["_snapshot_meta"] = {
            "saved_at": time.time(),
            "snapshot_version": "1.0",
        }
        
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(snapshot, ensure_ascii=False) + "\n")
        
        return path

    def load(self, graph_id: str) -> Optional[PTKG]:
        """
        [CITATION: PTKG-PERSISTENCE] Load the latest snapshot of a graph.
        Returns None if no snapshot exists.
        """
        path = self._graph_path(graph_id)
        if not path.exists():
            return None
        
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        if not lines:
            return None
        
        latest = json.loads(lines[-1])
        latest.pop("_snapshot_meta", None)
        
        return PTKG.from_dict(latest)

    def list_graphs(self) -> Dict[str, Dict[str, Any]]:
        """[CITATION: PTKG-PERSISTENCE] List all persisted graphs with metadata."""
        graphs = {}
        for path in self.storage_dir.glob("*.jsonl"):
            graph_id = path.stem
            stat = path.stat()
            with open(path, "r", encoding="utf-8") as f:
                snapshot_count = sum(1 for _ in f)
            graphs[graph_id] = {
                "path": str(path),
                "size_bytes": stat.st_size,
                "snapshot_count": snapshot_count,
                "last_modified": stat.st_mtime,
            }
        return graphs

    def compact(self, graph_id: str, keep_snapshots: Optional[int] = None) -> bool:
        """
        [CITATION: PTKG-PERSISTENCE] Compact a graph file by keeping only the latest N snapshots.
        Returns True if compaction occurred.
        """
        path = self._graph_path(graph_id)
        if not path.exists():
            return False
        
        keep = keep_snapshots or self.max_snapshots
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        if len(lines) <= keep:
            return False
        
        with open(path, "w", encoding="utf-8") as f:
            for line in lines[-keep:]:
                f.write(line)
        
        return True

    def delete(self, graph_id: str) -> bool:
        """[CITATION: PTKG-PERSISTENCE] Delete all snapshots for a graph."""
        path = self._graph_path(graph_id)
        if path.exists():
            path.unlink()
            return True
        return False
