#!/usr/bin/env bash
# Remote installer for vox — curl -fsSL <url> | bash
set -euo pipefail

REPO="almas-cp/vox2"
INSTALL_DIR="${HOME}/.local/bin"

info() { printf "\033[1;34m▸ %s\033[0m\n" "$*"; }
ok()   { printf "\033[1;32m✔ %s\033[0m\n" "$*"; }
err()  { printf "\033[1;31m✖ %s\033[0m\n" "$*" >&2; exit 1; }

main() {
  printf "\n\033[1m  ╦  ╦╔═╗═╗ ╦\n  ╚╗╔╝║ ║╔╩╦╝\n   ╚╝ ╚═╝╩ ╚═  installer\033[0m\n\n"

  command -v curl &>/dev/null   || err "curl is required"
  command -v python3 &>/dev/null || err "python3 is required (for URL encoding)"
  ok "deps: curl, python3"

  mkdir -p "$INSTALL_DIR"

  # Try latest GitHub release first, fall back to raw main branch
  local url
  url=$(curl -sf "https://api.github.com/repos/${REPO}/releases/latest" \
    | grep -o '"browser_download_url": *"[^"]*"' \
    | head -1 \
    | cut -d'"' -f4) 2>/dev/null || true

  if [[ -z "$url" ]]; then
    url="https://raw.githubusercontent.com/${REPO}/main/bin/vox"
    info "downloading from main branch"
  else
    info "downloading latest release"
  fi

  curl -fsSL "$url" -o "${INSTALL_DIR}/vox" || err "download failed"
  chmod +x "${INSTALL_DIR}/vox"
  ok "installed to ${INSTALL_DIR}/vox"

  # Check PATH
  if [[ ":$PATH:" != *":${INSTALL_DIR}:"* ]]; then
    printf "\n\033[1;33m⚠  Add to your shell profile:\033[0m\n"
    printf '   export PATH="%s:$PATH"\n\n' "$INSTALL_DIR"
  fi

  info "for best experience, add to .bashrc / .zshrc:"
  printf '   eval "$(vox init bash)"\n\n'

  ok "done! try: vox list all files"
}

main "$@"
