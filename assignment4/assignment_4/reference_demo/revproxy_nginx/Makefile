setup-python:
	cd flask_app; python -m pip install -r requirements.txt

build-flask-app:
	cd flask_app; docker pull python:3-slim
	cd flask_app; docker build -t flask_app .
	@echo "To remove dangling images: docker image prune"

test-lb:
	python test/clients.py
