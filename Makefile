.PHONY: setup.py requirements.txt

DIST_BASENAME := $(shell poetry version | tr ' ' '-')

all: precheck

develop: setup.py requirements.txt

setup.py:
	poetry build && \
	tar --strip-components=1 -xvf dist/$(DIST_BASENAME).tar.gz '*/setup.py'

requirements.txt:
	poetry export --without-hashes > requirements.txt

clean:
	rm -rf dist *.egg-info .pytest_cache
	rm -f requirements.txt setup.py
	rm -f poetry.lock

precheck:
	invoke precheck

.PHONY: tests
tests:
	cd tests && pytest -vvv
