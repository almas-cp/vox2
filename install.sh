#!/usr/bin/env bash
set -euo pipefail

REPO="https://github.com/your-org/vox-cli"
MIN_PYTHON="3.11"

info()  { printf "\033[1;34m▸ %s\033[0m\n" "$*"; }
ok()    { printf "\033[1;32m✔ %s\033[0m\n" "$*"; }
err()   { printf "\033[1;31m✖ %s\033[0m\n" "$*" >&2; exit 1; }

# --- Check Python version ---
check_python() {
    for cmd in python3 python; do
        if command -v "$cmd" &>/dev/null; then
            local ver
            ver=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
            if "$cmd" -c "import sys; exit(0 if sys.version_info >= (3,11) else 1)" 2>/dev/null; then
                PYTHON="$cmd"
                ok "Found $PYTHON ($ver)"
                return
            fi
        fi
    done
    err "Python >=$MIN_PYTHON is required. Install it first: sudo apt install python3"
}

# --- Install via pipx (preferred) or pip ---
install_vox() {
    if command -v pipx &>/dev/null; then
        info "Installing vox via pipx..."
        pipx install vox-cli 2>/dev/null || pipx install "git+${REPO}.git"
        ok "Installed via pipx"
    else
        info "pipx not found — installing via pip..."
        "$PYTHON" -m pip install --user vox-cli 2>/dev/null || \
            "$PYTHON" -m pip install --user "git+${REPO}.git"
        ok "Installed via pip (--user)"

        local user_bin
        user_bin=$("$PYTHON" -m site --user-base)/bin
        if [[ ":$PATH:" != *":$user_bin:"* ]]; then
            printf "\n\033[1;33m⚠  Add this to your shell profile:\033[0m\n"
            printf "   export PATH=\"%s:\$PATH\"\n\n" "$user_bin"
        fi
    fi
}

# --- Verify ---
verify() {
    if command -v vox &>/dev/null; then
        ok "vox is ready! Try: vox list all files"
    else
        info "Open a new terminal and run: vox --help"
    fi
}

main() {
    printf "\n\033[1m  ╦  ╦╔═╗═╗ ╦\n  ╚╗╔╝║ ║╔╩╦╝\n   ╚╝ ╚═╝╩ ╚═  installer\033[0m\n\n"
    check_python
    install_vox
    verify
}

main "$@"
