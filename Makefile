.PHONY: install
install:
	pip install -U pip setuptools poetry
	poetry install
	poetry run playwright install
	poetry run playwright install-deps

.PHONY: install-actions
install-actions:
	pip3 install -U pip setuptools poetry
	poetry config virtualenvs.create false
	poetry config experimental.new-installer false
	poetry install
	poetry run playwright install
	poetry run playwright install-deps

.PHONY: install-publish
install-publish:
	pip3 install -U pip setuptools poetry
#	poetry config virtualenvs.create false
#	poetry config experimental.new-installer false
#	poetry install

.PHONY: format
format:
	poetry run autoflake --remove-all-unused-imports --in-place -r --exclude __init__.py .
	poetry run isort .
	poetry run black .

.PHONY: lint
lint:
	poetry run autoflake --remove-all-unused-imports --in-place -r --exclude __init__.py --check .
	poetry run isort --check-only .
	poetry run black --check .
	poetry run pflake8 .
	poetry run mypy tests dude

.PHONY: test
test:
	poetry run pytest

.PHONY: tag
tag:
	VERSION=`poetry version | grep -o -E "\d+\.\d+\.\d+"`; \
	git tag -s -a $$VERSION -m "Release $$VERSION"
