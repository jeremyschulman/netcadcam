.PHONY: setup.py requirements.txt

DIST_BASENAME := $(shell poetry version | tr ' ' '-')

precheck: code-format code-check
	pre-commit run -a && \
	interrogate -c pyproject.toml

code-format:
	ruff format --config pyproject.toml $(CODE_DIRS)

code-check:
	ruff check --config pyproject.toml $(CODE_DIRS)

doc-check:
	interrogate -vvv $(PACKAGE_DIR) --omit-covered-files
