.PHONY: install dev lint test clean deb

install:
	pip install .

dev:
	pip install -e ".[dev]"

lint:
	ruff check vox/ tests/
	ruff format --check vox/ tests/

format:
	ruff format vox/ tests/
	ruff check --fix vox/ tests/

test:
	python -m pytest tests/ -v

clean:
	rm -rf build/ dist/ *.egg-info vox/*.pyc vox/__pycache__ tests/__pycache__
	rm -rf debian/vox-cli/ debian/*.debhelper* debian/*.substvars debian/files

deb:
	dpkg-buildpackage -us -uc -b
	@echo "Package built. Find .deb in parent directory."
