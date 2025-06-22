# btab2mxml

**btab2mxml** is a Python script that converts bass tablature (`.btab` files) to MusicXML format.  
Originally created to process tablatures from the [Rush Bass Tablature Project](http://www.cygnusproductions.com/rtp/bass/bass.asp).

---

## 🎯 Project Goals

- Convert textual bass tablatures into valid MusicXML files
- Preserve musical structure and integrity during conversion

---

## 🚀 Project Setup (using [Poetry](https://python-poetry.org/))

This project uses **Poetry** for dependency management and virtual environments.

### ✅ Prerequisites

Install Poetry (if not already installed):

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Optionally, configure Poetry to place virtual environments inside the project folder:

⚠️ This setting is global (affects all your projects), so only use it if you prefer .venv/ in each project.

```bash
poetry config virtualenvs.in-project true
```

Then install the project dependencies:

```bash
poetry install
```

### ▶️ Running the Script

Use the following command to display available options:

```bash
poetry run btab2mxml --help
```
Or run it directly (once inside the virtual environment):

```bash
poetry shell
btab2mxml path/to/your/file.btab
```

## 📝 License
This project is licensed under the GNU GPL v3.

⚠️ All tablature files remain the intellectual property of their respective original authors.
MusicXML conversions are provided for educational and personal use only.

## 📸 About
Project created in 2025 by Frédéric Cordonier.

## 🧩 Future ideas (optional section)

Export as musicXML tablatures instead of classic notation

---
