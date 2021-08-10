deps:  ## Install dependencies
	pip install black isort flake8
lint:
	black --check .
	## flake8 modeling forms.py main.py
format:
	isort --sl .
	black .
	flake8 modeling forms.py main.py --ignore E731,E266,F401,F841,E262,E501,W291
