# 🔊 Vox — Natural Language Shell Assistant

> Talk to your terminal. Vox translates plain English into shell commands using AI.
>
> One file. Zero dependencies beyond `curl` and `bash`.

```
$ vox find all python files modified today
```

```
╭──────────────────────────────────────────╮
│  find . -name "*.py" -mtime 0            │
╰──────────────────────────────────────────╯
  [E]xecute  [e]dit  [c]opy  [q]uit
```

```
$ vox
previous command: gcc -o main main.c
╭──────────────────────────────────────────╮
│  gcc -Wall -Wextra -o main main.c        │
╰──────────────────────────────────────────╯
  [E]xecute  [e]dit  [c]opy  [q]uit
```

---

## ✨ Features

- **Natural language → shell commands** — just describe what you want
- **No-args mode** — run `vox` alone to examine/fix your previous command
- **Safety first** — detects dangerous commands and warns before execution
- **Interactive prompt** — execute, edit, copy, or quit
- **Command history** — stored in `~/.vox_history`
- **Clipboard support** — xclip, xsel, wl-copy, pbcopy
- **Single file** — no virtualenv, no pip, no node_modules

## 📦 Installation

### One-liner

```bash
curl -fsSL https://raw.githubusercontent.com/almas-cp/vox2/main/install.sh | bash
```

### Manual

```bash
curl -o ~/.local/bin/vox https://raw.githubusercontent.com/almas-cp/vox2/main/bin/vox
chmod +x ~/.local/bin/vox
```

### From source

```bash
git clone https://github.com/almas-cp/vox2.git
cd vox2
make install
```

### Update

```bash
cd vox2
git pull
make install
```

## 🛠️ Setup (recommended)

For the **no-args** feature to reliably grab your previous command, add this to your shell profile:

```bash
# .bashrc or .zshrc
eval "$(vox init bash)"    # or: zsh, fish
```

This installs a tiny shell function that passes `$(fc -ln -1)` to vox. Without it, vox falls back to reading your history file (which requires `PROMPT_COMMAND="history -a"` in bash).

## 🚀 Usage

### Basic

```bash
vox list all files
vox kill process on port 3000
vox show disk usage sorted by size
vox compress this folder to tar.gz
```

### No-args — examine previous command

```bash
$ gcc -o main main.c      # you run something
$ vox                      # vox grabs it, sends to API, suggests a fix/improvement
```

### Flags

| Flag         | Description                |
|--------------|----------------------------|
| `--history`  | Show command history       |
| `--version`  | Show version               |
| `--help`     | Show help                  |

### Interactive Prompt

After generating a command, vox presents:

| Key | Action               |
|-----|----------------------|
| `E` | Execute the command  |
| `e` | Edit the command     |
| `c` | Copy to clipboard    |
| `q` | Quit                 |

## 🏗️ Architecture

```
bin/vox          ← the entire app (one bash script)
install.sh       ← one-liner installer
```

### Flow

1. User types `vox <query>` (or just `vox` for previous command)
2. Query is URL-encoded and sent to `https://vox.workers.dev/<query>`
3. API returns a shell command
4. Displayed in a box with ANSI colors
5. User picks: execute / edit / copy / quit
6. Saved to `~/.vox_history`

### Dependencies

| Dependency | Why                    | Pre-installed? |
|------------|------------------------|----------------|
| `bash`     | Script runtime         | ✅ everywhere  |
| `curl`     | API call               | ✅ everywhere  |
| `python3`  | URL encoding           | ✅ everywhere  |
| `grep`     | Dangerous cmd patterns | ✅ everywhere  |

Optional: `xclip`/`xsel`/`wl-copy` for clipboard support.

## 🛡️ Security

Vox detects dangerous patterns before execution:

- `rm -rf /` — recursive delete on root
- `mkfs` — disk formatting
- `dd if=` — raw disk writes
- `shutdown` / `reboot` — system control
- Fork bombs
- Piping remote scripts to shell — `curl ... | bash`

A **confirmation prompt** appears for flagged commands.

## 📄 License

MIT
