ifeq ($(shell id -u),0)
  PREFIX ?= /usr/local
else
  PREFIX ?= $(HOME)/.local
endif

SHELL_RC := $(wildcard $(HOME)/.bashrc)
ifeq ($(SHELL_RC),)
  SHELL_RC := $(wildcard $(HOME)/.zshrc)
endif

.PHONY: install uninstall

install:
	@mkdir -p $(PREFIX)/bin
	@cp bin/vox $(PREFIX)/bin/vox
	@chmod +x $(PREFIX)/bin/vox
	@echo "✔ installed to $(PREFIX)/bin/vox"
ifneq ($(SHELL_RC),)
	@if ! grep -q 'vox init' $(SHELL_RC) 2>/dev/null; then \
		echo '' >> $(SHELL_RC); \
		echo '# vox — natural language shell assistant' >> $(SHELL_RC); \
		echo 'eval "$$(vox init bash)"' >> $(SHELL_RC); \
		echo "✔ added shell function to $(SHELL_RC)"; \
		echo "  run: source $(SHELL_RC)"; \
	else \
		echo "✔ shell function already in $(SHELL_RC)"; \
	fi
endif

uninstall:
	@rm -f $(PREFIX)/bin/vox
	@echo "✔ removed $(PREFIX)/bin/vox"
