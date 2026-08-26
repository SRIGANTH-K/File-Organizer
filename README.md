# FileOrganizer

A small Python utility for sorting files into category folders.

## Features

- Uses a user-provided folder path instead of a hard-coded directory.
- Supports preview mode with `--dry-run`.
- Avoids overwriting existing files by automatically renaming conflicts.
- Organizes common file types into categories like Images, Videos, Audio, Documents, Spreadsheets, PowerPoint, Code, Archives, and Installers.
- Writes a log file for each run.
- Stores organize history so the last run can be undone with `--undo`.

## Usage

Preview what would happen:

```powershell
python organizer.py "D:\Downloads" --dry-run
```

Organize files:

```powershell
python organizer.py "D:\Downloads"
```

Undo the most recent organize run for that folder:

```powershell
python organizer.py "D:\Downloads" --undo
```

## Notes

- The tool only processes files directly inside the target folder.
- Generated history and log files are stored inside the target folder as `.fileorganizer_history.json` and `.fileorganizer.log`.
- Files that do not match a known extension are moved into `Other Files`.
