deps:  ## Install dependencies
	pip install black coverage flake8
lint:
	isort --sl -c .
	black --check .
	## flake8 modeling forms.py main.py
format:
	isort --sl .
	black .
	flake8 modeling forms.py main.py --ignore E731,E266,F401,F841,E262,E501,W291
