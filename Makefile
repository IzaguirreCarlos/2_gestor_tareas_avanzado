.PHONY: run migrate migrations shell test collectstatic install

run:
	python manage.py runserver

migrate:
	python manage.py migrate

migrations:
	python manage.py makemigrations

shell:
	python manage.py shell

test:
	python manage.py test apps

collectstatic:
	python manage.py collectstatic --noinput

install:
	pip install -r requirements/development.txt

install-prod:
	pip install -r requirements/production.txt
