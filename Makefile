PREFIX ?= $(HOME)/.local

.PHONY: install uninstall

install:
	@mkdir -p $(PREFIX)/bin
	@cp bin/vox $(PREFIX)/bin/vox
	@chmod +x $(PREFIX)/bin/vox
	@echo "✔ installed to $(PREFIX)/bin/vox"
	@echo ""
	@echo "Add to .bashrc / .zshrc:"
	@echo '  eval "$$(vox init bash)"'

uninstall:
	@rm -f $(PREFIX)/bin/vox
	@echo "✔ removed $(PREFIX)/bin/vox"
