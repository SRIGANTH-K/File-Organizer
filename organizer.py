import argparse
import json
import logging
import shutil
from collections import Counter
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

CATEGORY_MAP = [
    ("Images", {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tif", ".tiff", ".svg"}),
    ("Videos", {".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv", ".webm"}),
    ("Audio", {".mp3", ".wav", ".aac", ".flac", ".m4a", ".ogg"}),
    ("Documents", {".pdf", ".txt", ".doc", ".docx", ".rtf", ".odt"}),
    ("Spreadsheets", {".xls", ".xlsx", ".csv", ".ods"}),
    ("PowerPoint", {".ppt", ".pptx", ".odp"}),
    ("Code", {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".c", ".cpp", ".h", ".hpp", ".cs", ".rb", ".go", ".rs", ".php", ".sh", ".bat", ".ps1", ".json", ".html", ".htm", ".css", ".xml", ".yml", ".yaml", ".md", ".sql"}),
    ("Archives", {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"}),
    ("Installers", {".exe", ".msi", ".pkg", ".dmg", ".deb", ".rpm"}),
]

HISTORY_FILE_NAME = ".fileorganizer_history.json"
LOG_FILE_NAME = ".fileorganizer.log"


@dataclass
class MoveRecord:
    source: str
    destination: str
    category: str


@dataclass
class SessionRecord:
    id: str
    timestamp: str
    root: str
    dry_run: bool
    undone: bool
    operations: list[MoveRecord]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Organize files into category folders, preview moves, and undo the last run."
    )
    parser.add_argument("folder", help="Folder to organize")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the moves without changing any files",
    )
    parser.add_argument(
        "--undo",
        action="store_true",
        help="Undo the most recent organize run for this folder",
    )
    return parser


def get_root(folder: str) -> Path:
    root = Path(folder).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Folder not found: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Not a folder: {root}")
    return root


def category_for_file(path: Path) -> str | None:
    suffix = path.suffix.lower()
    for category, extensions in CATEGORY_MAP:
        if suffix in extensions:
            return category
    return "Other Files" if suffix or path.name else None


def ensure_folder(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def safe_destination(target: Path) -> Path:
    if not target.exists():
        return target

    stem = target.stem
    suffix = target.suffix
    parent = target.parent
    index = 1
    while True:
        candidate = parent / f"{stem}_{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def iter_source_files(root: Path) -> Iterable[Path]:
    for path in root.iterdir():
        if path.is_file() and path.name not in {HISTORY_FILE_NAME, LOG_FILE_NAME}:
            yield path


def history_path(root: Path) -> Path:
    return root / HISTORY_FILE_NAME


def log_path(root: Path) -> Path:
    return root / LOG_FILE_NAME


def load_history(root: Path) -> list[dict]:
    path = history_path(root)
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_history(root: Path, sessions: list[dict]) -> None:
    history_path(root).write_text(json.dumps(sessions, indent=2), encoding="utf-8")


def configure_logging(root: Path) -> None:
    ensure_folder(root)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file_handler = logging.FileHandler(log_path(root), encoding="utf-8")
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


def organize(root: Path, dry_run: bool) -> int:
    configure_logging(root)
    files = list(iter_source_files(root))
    planned: list[MoveRecord] = []

    for file_path in files:
        category = category_for_file(file_path)
        if not category:
            continue
        destination_dir = root / category
        destination = safe_destination(destination_dir / file_path.name)
        planned.append(MoveRecord(str(file_path), str(destination), category))

    if not planned:
        print("No files matched a category.")
        return 0

    counts = Counter(record.category for record in planned)
    for record in planned:
        action = "Would move" if dry_run else "Moved"
        print(f"{action}: {Path(record.source).name} -> {record.category}/{Path(record.destination).name}")

    summary = ", ".join(f"{category}: {count}" for category, count in sorted(counts.items()))
    print(f"Planned {len(planned)} file(s). {summary}")

    if dry_run:
        logging.info("Dry run completed with %d planned move(s).", len(planned))
        return len(planned)

    for record in planned:
        source = Path(record.source)
        destination = Path(record.destination)
        ensure_folder(destination.parent)
        shutil.move(str(source), str(destination))
        logging.info("Moved %s -> %s", source, destination)

    sessions = load_history(root)
    sessions.append(
        asdict(
            SessionRecord(
                id=datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f"),
                timestamp=datetime.now(timezone.utc).isoformat(),
                root=str(root),
                dry_run=False,
                undone=False,
                operations=planned,
            )
        )
    )
    save_history(root, sessions)
    logging.info("Recorded session with %d move(s).", len(planned))
    return len(planned)


def undo_last(root: Path) -> int:
    configure_logging(root)
    sessions = load_history(root)
    for session in reversed(sessions):
        if not session.get("dry_run") and not session.get("undone"):
            operations = session.get("operations", [])
            moved_back = 0
            for record in reversed(operations):
                destination = Path(record["destination"])
                original = Path(record["source"])
                if not destination.exists():
                    logging.warning("Missing file during undo: %s", destination)
                    continue
                restore_target = safe_destination(original)
                ensure_folder(restore_target.parent)
                shutil.move(str(destination), str(restore_target))
                logging.info("Restored %s -> %s", destination, restore_target)
                moved_back += 1

            session["undone"] = True
            save_history(root, sessions)
            print(f"Undid {moved_back} file(s) from the last organize run.")
            return moved_back

    print("No completed organize run found to undo.")
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    root = get_root(args.folder)

    if args.undo:
        undo_last(root)
        return 0

    organize(root, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
