# FileOrganizer

> 🧹 Organize messy folders with one command, preview changes before you move anything, and keep your cleanup reversible.

A simple Python tool for sorting files into neat category folders, avoiding overwrites, logging every run, and undoing the last organize session when needed.

## ✨ Highlights

- 🚀 User-controlled folder path instead of a hard-coded directory
- 👀 Preview mode with `--dry-run`
- 🛡️ Safe renaming so existing files are never overwritten
- 🗂️ Smart categories for Images, Videos, Audio, Documents, Spreadsheets, PowerPoint, Code, Archives, and Installers
- 🧾 Run history and log files for traceability
- ↩️ Undo support for the last organize run

## 🐍 Language

| Item | Value |
|---|---|
| Language | `Python` |
| Style | Command-line utility |
| Focus | File organization and cleanup |

## 📸 Screenshots

### Preview of the organization

```powershell
python organizer.py "D:\Downloads" --dry-run
```

![Preview of the organization](images/preview-organization.png)

### Before organizing

```powershell
python organizer.py "D:\Downloads"
```

![Before organizing](images/before-organizing.png)

### After organized

```powershell
python organizer.py "D:\Downloads"
```

![After organized](images/after-organized.png)

### Organized history

```powershell
python organizer.py "D:\Downloads" --undo
```

![Organized history](images/organized-history.png)

## 🧭 How It Works

1. Choose the folder you want to clean up.
2. The script scans the files directly inside that folder.
3. Each file is matched to a category based on its extension.
4. In preview mode, you see what would happen without moving files.
5. In normal mode, files are moved into folders and the session is recorded for undo.

## ⚡ Quick Examples

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

## 📁 Output Files

- `.fileorganizer_history.json` stores undo history
- `.fileorganizer.log` stores the run log
- Category folders such as `Images`, `Documents`, and `Code` are created inside the folder you choose

## 👨‍💻 Author

### Sri Ganth K

| Platform | Link |
|---|---|
| 💼 LinkedIn | [Sri Ganth K](https://www.linkedin.com/in/sri-ganth-k) |
| 🐙 GitHub | [SRIGANTH-K](https://github.com/SRIGANTH-K) |
| 📷 Instagram | [sri_ganth_k](https://www.instagram.com/sri_ganth_k) |

---

⭐ If you find this project useful, give it a star and share it with someone who needs a cleaner Downloads folder.

Built with `Python` and a little love for tidy folders.

## ✅ Notes

- The tool only processes files directly inside the target folder.
- Files that do not match a known extension are moved into `Other Files`.
- If a file name already exists in a category folder, the new file is renamed safely instead of replacing the old one.
