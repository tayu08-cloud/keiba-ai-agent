from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Horse:
    """Minimal horse model for parsed JV-Link JG records.

    The parser keeps the minimum fields required now while leaving room for
    future expansion such as horse_id, sex, age, trainer, owner, and breeder.
    """

    horse_name: str | None = None
    record_type: str | None = None
    raw: str | None = None
    horse_id: str | None = None
    sex: str | None = None
    age: int | None = None
    trainer: str | None = None
    owner: str | None = None
    breeder: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "horse_name": self.horse_name,
            "record_type": self.record_type,
            "raw": self.raw,
            "horse_id": self.horse_id,
            "sex": self.sex,
            "age": self.age,
            "trainer": self.trainer,
            "owner": self.owner,
            "breeder": self.breeder,
            "extra": self.extra,
        }


def parse_jg_record(raw: str) -> Horse:
    """Parse a fixed-length JV-Link JG record into a Horse dataclass."""
    cleaned = raw.rstrip("\r\n")

    if len(cleaned) < 2:
        raise ValueError("JG record is too short.")

    record_type = cleaned[:2]
    if record_type != "JG":
        raise ValueError(f"Unsupported record type: {record_type}")

    candidates = _extract_name_candidates(cleaned)
    horse_name = candidates[0] if candidates else None

    return Horse(
        horse_name=horse_name,
        record_type=record_type,
        raw=cleaned,
        extra={"horse_name_candidates": candidates},
    )


def _extract_name_candidates(raw: str) -> list[str]:
    body = raw[2:]
    candidates: list[str] = []

    for match in re.finditer(r"[A-Za-z\u3040-\u30ff\u3400-\u9fff\uff66-\uff9fー・\u3000 ]+", body):
        candidate = match.group(0).replace("\u3000", " ").strip()
        candidate = re.sub(r"\s+", " ", candidate)

        if len(candidate) >= 2 and any(not ch.isdigit() and not ch.isspace() for ch in candidate):
            candidates.append(candidate)

    return candidates
