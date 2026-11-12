#!/usr/bin/env python3
"""
EK_C_0.3 - minimális, futtatható referencia-prototípus.

Funkciók:
- hierarchikus Category -> Topic -> Pointer modell
- SQLite perzisztencia
- write-back PointerCache
- külön policy JSON
- 0. szabály előellenőrzés
- pointer-relációk
- conflict resolver: rangsorol, nem dönt véglegesen
- központi SYSERR log
- bizonytalanság/hiány esetén jelzés, nem kitalálás

Megjegyzés:
A policy itt demonstrációs tartalmi kapu. Nem helyettesít
egy teljes biztonsági/moderációs rendszert.
"""

from __future__ import annotations

import json
import logging
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional


ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "ek.db"
POLICY_PATH = ROOT / "ek_policy.json"
LOG_PATH = ROOT / "ek_syserr.log"

VALID_RELATIONS = {
    "Related",
    "Parent",
    "Child",
    "DependsOn",
    "Source",
    "Similar",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log_syserr(component: str, message: str) -> None:
    line = f"SYSERR: {utc_now()} :: {component}: {message}"
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


@dataclass
class Pointer:
    id: int
    category: str
    topic: str
    source: str
    summary: str
    last_checked: Optional[str] = None
    confidence: Optional[float] = None


class Policy:
    def __init__(self, path: Path = POLICY_PATH) -> None:
        self.path = path
        self.data = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            raise FileNotFoundError(f"Policy file not found: {self.path}")
        with self.path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def precheck(self, text: str) -> tuple[bool, list[str]]:
        """
        Egyszerű demonstrációs hard gate.
        A policy kulcsszavakat tartalmazhat; találat esetén BLOCK.
        """
        normalized = text.casefold()
        hits: list[str] = []

        for term in self.data.get("blocked_terms", []):
            if term.casefold() in normalized:
                hits.append(term)

        return (not hits, hits)


class EKStore:
    def __init__(
        self,
        db_path: Path = DB_PATH,
        policy_path: Path = POLICY_PATH,
        flush_every: int = 10,
    ) -> None:
        self.db_path = db_path
        self.policy = Policy(policy_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cache = PointerCache(self, flush_every=flush_every)
        self._init_db()

    def _init_db(self) -> None:
        try:
            self.conn.executescript(
                """
                PRAGMA foreign_keys = ON;

                CREATE TABLE IF NOT EXISTS pointers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    source TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    last_checked TEXT,
                    confidence REAL
                );

                CREATE INDEX IF NOT EXISTS idx_pointer_category_topic
                    ON pointers(category, topic);

                CREATE TABLE IF NOT EXISTS relations (
                    source_id INTEGER NOT NULL,
                    target_id INTEGER NOT NULL,
                    relation TEXT NOT NULL,
                    PRIMARY KEY(source_id, target_id, relation),
                    FOREIGN KEY(source_id) REFERENCES pointers(id) ON DELETE CASCADE,
                    FOREIGN KEY(target_id) REFERENCES pointers(id) ON DELETE CASCADE
                );
                """
            )
            self.conn.commit()
        except Exception as exc:
            log_syserr("DB", f"initialization failed: {exc}")
            raise

    def add_pointer(
        self,
        category: str,
        topic: str,
        source: str,
        summary: str,
        last_checked: Optional[str] = None,
        confidence: Optional[float] = None,
    ) -> int:
        if not all([category.strip(), topic.strip(), source.strip(), summary.strip()]):
            raise ValueError("category/topic/source/summary are required")

        if confidence is not None and not (0 <= confidence <= 100):
            raise ValueError("confidence must be between 0 and 100")

        pointer = {
            "category": category,
            "topic": topic,
            "source": source,
            "summary": summary,
            "last_checked": last_checked,
            "confidence": confidence,
        }
        self.cache.put(pointer)
        return self.cache.pending[-1]["_cache_id"]

    def _insert_pointer(self, data: dict[str, Any]) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO pointers
            (category, topic, source, summary, last_checked, confidence)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data["category"],
                data["topic"],
                data["source"],
                data["summary"],
                data.get("last_checked"),
                data.get("confidence"),
            ),
        )
        return int(cur.lastrowid)

    def flush(self) -> None:
        self.cache.flush()

    def search(self, query: str, limit: int = 10) -> list[Pointer]:
        """
        Egyszerű lexikális retrieval. Nem vektoros kereső.
        """
        allowed, hits = self.policy.precheck(query)
        if not allowed:
            log_syserr("POLICY", f"query blocked; terms={hits}")
            return []

        tokens = [
            t for t in re.findall(r"\w+", query.casefold())
            if len(t) >= 2
        ]

        rows = self.conn.execute(
            """
            SELECT id, category, topic, source, summary, last_checked, confidence
            FROM pointers
            """
        ).fetchall()

        scored: list[tuple[float, sqlite3.Row]] = []
        for row in rows:
            haystack = " ".join(
                [
                    row["category"] or "",
                    row["topic"] or "",
                    row["summary"] or "",
                ]
            ).casefold()

            score = sum(1 for token in tokens if token in haystack)
            if score > 0:
                scored.append((float(score), row))

        scored.sort(
            key=lambda item: (
                item[0],
                item[1]["confidence"] or 0,
                item[1]["last_checked"] or "",
            ),
            reverse=True,
        )

        return [
            Pointer(
                id=row["id"],
                category=row["category"],
                topic=row["topic"],
                source=row["source"],
                summary=row["summary"],
                last_checked=row["last_checked"],
                confidence=row["confidence"],
            )
            for _, row in scored[:limit]
        ]

    def add_relation(self, source_id: int, target_id: int, relation: str) -> None:
        if relation not in VALID_RELATIONS:
            msg = f"invalid relation type: {relation}"
            log_syserr("RELATION", msg)
            raise ValueError(msg)

        self.conn.execute(
            """
            INSERT OR IGNORE INTO relations(source_id, target_id, relation)
            VALUES (?, ?, ?)
            """,
            (source_id, target_id, relation),
        )
        self.conn.commit()

    def get_relations(self, pointer_id: int) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT r.relation, r.target_id,
                   p.category, p.topic, p.source, p.summary
            FROM relations r
            JOIN pointers p ON p.id = r.target_id
            WHERE r.source_id = ?
            """,
            (pointer_id,),
        ).fetchall()

        return [dict(row) for row in rows]

    def resolve_conflict(self, pointers: Iterable[Pointer]) -> dict[str, Any]:
        """
        Csak rangsorolási javaslat.
        Nem állítja, hogy a legmagasabb pontszámú pointer biztosan igaz.
        """
        items = list(pointers)
        if not items:
            return {
                "status": "NO_RESULT",
                "message": "Nincs releváns EK pointer.",
                "recommendation": None,
            }

        ranked = sorted(
            items,
            key=lambda p: (
                p.confidence if p.confidence is not None else -1,
                p.last_checked or "",
            ),
            reverse=True,
        )

        return {
            "status": "REVIEW_REQUIRED",
            "message": "A találatok rangsorolva vannak; végső választás nem történik automatikusan.",
            "recommendation": ranked[0].id,
            "ranked_ids": [p.id for p in ranked],
        }

    def close(self) -> None:
        try:
            self.flush()
            self.conn.close()
        except Exception as exc:
            log_syserr("DB", f"close failed: {exc}")


class PointerCache:
    def __init__(self, store: EKStore, flush_every: int = 10) -> None:
        self.store = store
        self.flush_every = max(1, flush_every)
        self.pending: list[dict[str, Any]] = []
        self._next_cache_id = -1

    def put(self, pointer: dict[str, Any]) -> None:
        item = dict(pointer)
        item["_cache_id"] = self._next_cache_id
        self._next_cache_id -= 1
        self.pending.append(item)

        if len(self.pending) >= self.flush_every:
            self.flush()

    def flush(self) -> None:
        if not self.pending:
            return

        try:
            for item in self.pending:
                item.pop("_cache_id", None)
                self.store._insert_pointer(item)
            self.store.conn.commit()
            self.pending.clear()
        except Exception as exc:
            self.store.conn.rollback()
            log_syserr("CACHE", f"flush failed: {exc}")
            raise


def demo() -> None:
    store = EKStore(flush_every=3)

    a = store.add_pointer(
        "Tudomány_Űr",
        "Nap_és_égés",
        "https://science.nasa.gov/sun",
        "A Nap energiatermelése nukleáris fúzióhoz kapcsolódik, nem kémiai égéshez.",
        "2026-03-17",
        98,
    )

    b = store.add_pointer(
        "Technológia_AI",
        "EK_rendszer",
        "internal_EK_system",
        "Hierarchikus pointer-alapú külső memória; retrieval és metaadatok.",
        "2026-08-08",
        100,
    )

    # A flush_every=3 miatt még nem biztos, hogy mindkettő DB-ben van.
    store.flush()

    results = store.search("EK pointer külső memória")
    print("Találatok:")
    for item in results:
        print(f"- [{item.id}] {item.category}/{item.topic} :: {item.source}")

    decision = store.resolve_conflict(results)
    print("\nConflict Resolver:")
    print(json.dumps(decision, ensure_ascii=False, indent=2))

    # Kapcsolat példa:
    if a > 0 and b > 0:
        store.add_relation(b, a, "Related")

    store.close()


if __name__ == "__main__":
    demo()
