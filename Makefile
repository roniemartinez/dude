.PHONY: install
install:
	pip3 install -U pip setuptools poetry
	poetry install -E bs4 -E parsel -E lxml -E pyppeteer -E selenium
	poetry run playwright install
	poetry run playwright install-deps

.PHONY: install-actions
install-actions:
	pip3 install pip setuptools poetry
	poetry config virtualenvs.create false
	poetry config experimental.new-installer false
	poetry install -E bs4 -E parsel -E lxml -E pyppeteer -E selenium
	poetry run playwright install
	poetry run playwright install-deps

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
	VERSION=`poetry version | grep -o -E "\d+\.\d+\.\d+(-\w+\.\d+)?"`; \
	git tag -s -a $$VERSION -m "Release $$VERSION"; \
	echo "Tagged $$VERSION";

.PHONY: serve-mkdocs
serve-mkdocs:
	poetry run mkdocs serve
