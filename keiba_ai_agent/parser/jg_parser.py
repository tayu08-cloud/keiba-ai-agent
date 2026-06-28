import re


def parse_jg_record(raw: str) -> dict:
    """Parse the minimum fields from a JV-Link JG raw record.

    This parser is intentionally conservative. It keeps the original raw text
    and only extracts fields that can be identified safely from current samples.
    """
    cleaned = raw.rstrip("\r\n")

    if len(cleaned) < 2:
        raise ValueError("JG record is too short.")

    record_type = cleaned[:2]
    if record_type != "JG":
        raise ValueError(f"Unsupported record type: {record_type}")

    candidates = _extract_name_candidates(cleaned)

    return {
        "record_type": record_type,
        "raw": cleaned,
        "name": candidates[0] if candidates else None,
        "horse_name_candidates": candidates,
    }


def _extract_name_candidates(raw: str) -> list[str]:
    body = raw[2:]
    candidates: list[str] = []

    for match in re.finditer(r"[A-Za-z\u3040-\u30ff\u3400-\u9fff\uff66-\uff9fー・\u3000 ]+", body):
        candidate = match.group(0).replace("\u3000", " ").strip()
        candidate = re.sub(r"\s+", " ", candidate)

        if len(candidate) >= 2 and any(not ch.isdigit() and not ch.isspace() for ch in candidate):
            candidates.append(candidate)

    return candidates
