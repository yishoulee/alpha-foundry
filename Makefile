.PHONY: install run test clean help

PYTHON = python3

help:
	@echo "Available commands:"
	@echo "  make install   - Install dependencies"
	@echo "  make run       - Run the backtesting engine"
	@echo "  make test      - Run unit tests"
	@echo "  make clean     - Remove temporary files and cached data"

install:
	pip install -r requirements.txt

run:
	$(PYTHON) main.py

test:
	$(PYTHON) -m unittest discover tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf results/*.png
