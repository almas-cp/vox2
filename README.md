# 🔊 Vox — Natural Language Shell Assistant

> Talk to your terminal. Vox translates plain English into shell commands using AI.

```
$ vox find all python files modified today
```

```
╭──────────────────────────────────────────╮
│  GENERATED COMMAND                       │
│                                          │
│  find . -name "*.py" -mtime 0            │
│                                          │
╰──────────────────────────────────────────╯
  [E]xecute  [e]dit  [c]opy  [q]uit
```

---

## ✨ Features

- **Natural language → shell commands** — just describe what you want
- **Rich CLI output** — syntax-highlighted commands in styled panels
- **Safety first** — detects dangerous commands (`rm -rf /`, `mkfs`, etc.) and warns before execution
- **Command history** — searchable, with favorites, stored in `~/.vox_history.json`
- **Clipboard support** — copy commands with a single keystroke
- **Shell-aware** — auto-detects bash, zsh, fish
- **Distro-aware** — sends OS info for better command generation

## 📦 Installation

### pip (recommended)

```bash
pip install vox-cli
```

### pipx (isolated environment)

```bash
pipx install vox-cli
```

### One-line installer

```bash
curl -fsSL https://example.com/install.sh | bash
```

### From source

```bash
git clone https://github.com/your-org/vox-cli.git
cd vox-cli
pip install -e ".[dev]"
```

### Debian package

```bash
# Build .deb (requires dpkg-buildpackage)
make deb

# Install
sudo dpkg -i ../vox-cli_1.0.0-1_all.deb
```

## 🚀 Usage

### Basic

```bash
vox list all files
vox kill process on port 3000
vox show disk usage sorted by size
vox compress this folder to tar.gz
```

### Flags

| Flag         | Description                              |
|--------------|------------------------------------------|
| `--explain`  | Show explanation of the generated command |
| `--dry-run`  | Show command without executing            |
| `--history`  | Show command history                      |
| `--voice`    | Voice input mode (coming soon)            |
| `--version`  | Show version                              |

### Examples

```bash
# Dry run — see command without executing
vox --dry-run delete all .log files

# Explain what the command does
vox --explain set up a python virtual environment

# View past commands
vox --history
```

### Interactive Prompt

After generating a command, vox presents an action menu:

| Key | Action                     |
|-----|----------------------------|
| `E` | Execute the command        |
| `e` | Edit the command           |
| `c` | Copy to clipboard          |
| `q` | Quit                       |

## 🏗️  Architecture

```
vox/
├── cli.py        # Typer entry point, flag parsing, interactive prompt
├── api.py        # httpx client with retry logic
├── executor.py   # Subprocess runner
├── security.py   # Dangerous command detection (regex-based)
├── history.py    # JSON-backed command history
├── clipboard.py  # pyperclip wrapper with fallback
└── utils.py      # Shell & distro detection
```

### Flow

1. User types `vox <query>`
2. CLI joins args → sends query to `https://vox.workers.dev/<query>`
3. API returns a shell command
4. CLI displays command with syntax highlighting in a Rich panel
5. User picks an action → execute / edit / copy / quit
6. Entry saved to history

## 🛡️  Security

Vox detects dangerous patterns before execution:

- `rm -rf /` — recursive delete on root
- `mkfs` — disk formatting
- `dd if=` — raw disk writes
- `shutdown` / `reboot` — system control
- Fork bombs — `:(){ :|:& };:`
- Piping remote scripts to shell — `curl ... | bash`

A **confirmation prompt** appears for flagged commands. You can still execute — but must confirm.

## 🧑‍💻 Development

```bash
# Clone and set up
git clone https://github.com/your-org/vox-cli.git
cd vox-cli
make dev

# Run tests
make test

# Lint
make lint

# Format
make format
```

## 📄 License

MIT
