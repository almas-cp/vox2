Create a production-ready Linux CLI application named `vox` that works as a natural-language-to-shell-command assistant using the following API endpoint:

https://vox.workers.dev/<query>

Example API usage:

curl "https://vox.workers.dev/list all files"
curl "https://vox.workers.dev/find python files modified today"
curl "https://vox.workers.dev/compress this folder to tar.gz"

The app must be installable on Debian/Ubuntu systems and callable globally from terminal like:

vox create a directory named hw
vox kill process on port 3000
vox show disk usage sorted by size

====================
CORE REQUIREMENTS
=================

1. LANGUAGE & STACK

* Use Python 3.11+
* Use:

  * Textual for TUI
  * Typer for CLI
  * Rich for styling/output
  * Requests or HTTPX for API calls

2. APP BEHAVIOR
   When the user runs:

vox create a directory named hw

the app should:

* send the query to:
  https://vox.workers.dev/create%20a%20directory%20named%20hw
* receive shell command response
* display it beautifully in a terminal UI
* allow:

  * execute
  * edit
  * copy
  * cancel

3. TUI FEATURES
   Build a polished modern TUI interface with:

* bordered command preview panel
* keyboard shortcuts
* editable command input box
* execution logs section
* command history sidebar
* syntax-highlighted shell commands
* loading animation while requesting API
* status footer

Keyboard shortcuts:

* Enter → execute
* e → edit
* c → copy
* q → quit
* h → history

4. SECURITY
   Implement safety protections:

* detect dangerous commands
* show warning modal before execution for risky commands

Flag dangerous patterns like:

* rm -rf /
* mkfs
* dd if=
* shutdown
* reboot
* fork bombs

Allow user to override manually.

5. EXECUTION

* execute commands locally using subprocess
* stream stdout/stderr live into TUI
* support long-running commands
* preserve colors if possible

6. HISTORY
   Store query + generated command history in:
   ~/.vox_history.json

Features:

* searchable history
* rerun previous command
* favorite commands

7. CLIPBOARD
   Add clipboard support using pyperclip.

8. SHELL DETECTION
   Auto-detect:

* bash
* zsh
* fish

9. OS DETECTION
   Detect Linux distro and send it as optional header:

* Debian
* Ubuntu
* Arch
* Fedora

10. PACKAGING
    Make it:

* pip installable
* Debian package installable
* executable globally as:
  vox

Generate:

* pyproject.toml
* setup.py
* Makefile
* .deb packaging support

11. INSTALLER
    Create:
    install.sh

that installs the app globally with:

curl -fsSL https://example.com/install.sh | bash

12. PROJECT STRUCTURE

Use this structure:

vox-cli/
├── vox/
│   ├── **init**.py
│   ├── cli.py
│   ├── tui.py
│   ├── api.py
│   ├── executor.py
│   ├── security.py
│   ├── history.py
│   ├── clipboard.py
│   └── utils.py
├── tests/
├── pyproject.toml
├── setup.py
├── Makefile
├── README.md
└── install.sh

13. CODE QUALITY

* type hints everywhere
* modular architecture
* production-ready code
* proper exception handling
* retry logic for API failures
* async support if useful
* lint-friendly
* include comments only where useful

14. README
    Generate a high-quality README including:

* screenshots placeholders
* install instructions
* usage examples
* keyboard shortcuts
* architecture explanation
* development setup
* Debian packaging instructions

15. EXTRA FEATURES
    If possible also add:

* --explain flag to explain generated command
* --dry-run mode
* voice mode placeholder
* streaming AI responses support
* themes (dark/light terminal)
* autocomplete support
* sandbox execution mode
* offline fallback messages

16. UX GOAL
    The final app should feel like:

* lazygit
* btop
* gh CLI
* modern polished hacker-style terminal app

17. IMPORTANT

* Do NOT auto-execute commands without confirmation
* Prioritize safety and UX
* Make the UI visually impressive
* Ensure the app works well on Debian systems
* Make all code complete and runnable
* Generate all required files fully
* Do not leave TODO placeholders

Output the complete project codebase file-by-file.
