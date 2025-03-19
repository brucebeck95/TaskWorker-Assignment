run:
	docker-compose up --build -d

test:
	docker-compose start db; export DATABASE_URL="postgresql://app_user:dummy_password@0.0.0.0:5432/app"; pytest -vvv tests/

mypy:
	mypy app --show-error-codes --ignore-missing-imports --warn-unused-ignores --check-untyped-defs --disallow-incomplete-defs

clean:
	docker rm -v -f $(docker ps -qa)
