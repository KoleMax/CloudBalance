setup-dev-env:
	python -m gino.ext stub

migration:
	alembic revision --autogenerate -m $(name)

migrate:
	alembic upgrade head

lint:
	flake8 .
	black .
	pylint ./application

test:
	pytest -s -vv ./tests

install-hook:
	pre-commit install
.PHONY: install-hook

uninstall-hook:
	pre-commit uninstall
.PHONY: uninstall-hook