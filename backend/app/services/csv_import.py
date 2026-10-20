"""CSV transaction import. Validates and parses rows into Transaction records.
Idempotent: a row's import_reference is a hash of its raw fields, so
re-importing the same file does not create duplicates.
"""
from __future__ import annotations

import csv
import hashlib
import io
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

REQUIRED_COLUMNS = {"date", "amount", "direction", "category"}
DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y")


@dataclass
class ImportRowError:
    row_number: int
    reason: str


@dataclass
class ParsedRow:
    date: date
    amount: Decimal
    direction: str
    category: str
    description: str
    import_reference: str


@dataclass
class ImportResult:
    valid_rows: list[ParsedRow] = field(default_factory=list)
    errors: list[ImportRowError] = field(default_factory=list)


def _parse_date(raw: str) -> date | None:
    raw = raw.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def _row_hash(row: dict) -> str:
    key = "|".join(str(row.get(c, "")) for c in ["date", "amount", "direction", "category", "description"])
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:32]


def parse_csv(content: bytes) -> ImportResult:
    result = ImportResult()
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        result.errors.append(ImportRowError(0, "File is not valid UTF-8 text"))
        return result

    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        result.errors.append(ImportRowError(0, "CSV has no header row"))
        return result

    columns = {c.strip().lower() for c in reader.fieldnames}
    missing = REQUIRED_COLUMNS - columns
    if missing:
        result.errors.append(
            ImportRowError(0, f"Missing required column(s): {', '.join(sorted(missing))}")
        )
        return result

    for idx, raw_row in enumerate(reader, start=2):  # header is row 1
        row = {k.strip().lower(): (v.strip() if v else "") for k, v in raw_row.items()}

        parsed_date = _parse_date(row.get("date", ""))
        if not parsed_date:
            result.errors.append(ImportRowError(idx, f"Invalid or unparseable date: '{row.get('date')}'"))
            continue

        try:
            amount = Decimal(row.get("amount", "").replace(",", ""))
        except (InvalidOperation, AttributeError):
            result.errors.append(ImportRowError(idx, f"Invalid amount: '{row.get('amount')}'"))
            continue
        if amount <= 0:
            result.errors.append(ImportRowError(idx, "Amount must be positive (use 'direction' for sign)"))
            continue

        direction = row.get("direction", "").upper()
        if direction not in ("IN", "OUT"):
            result.errors.append(ImportRowError(idx, f"Direction must be IN or OUT, got '{row.get('direction')}'"))
            continue

        category = row.get("category", "").strip() or "uncategorized"
        description = row.get("description", "")

        result.valid_rows.append(
            ParsedRow(
                date=parsed_date,
                amount=amount,
                direction=direction,
                category=category,
                description=description,
                import_reference=_row_hash(row),
            )
        )

    return result
