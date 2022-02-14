.PHONY: install
install:
	pip install -U pip setuptools poetry
	poetry install
	poetry run playwright install
