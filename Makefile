.PHONY: help setup sync hooks env db migrate superuser run test lint down

help:
	@printf '%s\n' \
		'make setup      처음 한 번. 의존성, git hook, Postgres, 마이그레이션, 샘플 데이터' \
		'make superuser  관리자 계정. DB를 켜고 마이그레이션한 뒤 아이디와 비밀번호를 묻습니다' \
		'make run        개발 서버 http://127.0.0.1:8000/' \
		'make test       pytest. Postgres가 꺼져 있으면 켭니다' \
		'make lint       ruff와 ty. 데이터베이스는 쓰지 않습니다' \
		'make down       Postgres 중지'

setup: sync hooks env db migrate

sync:
	uv sync

hooks:
	uv run pre-commit install

env:
	@test -f .env || cp .env.example .env

db: env
	docker compose up -d --wait

migrate: env
	uv run python manage.py migrate

superuser: db migrate
	uv run python manage.py createsuperuser

run: env
	uv run python manage.py runserver 127.0.0.1:8000

test: db
	uv run pytest

lint:
	uv run ruff format --check .
	uv run ruff check .
	uv run ty check

down:
	docker compose down
