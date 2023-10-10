PYTHON = python3
VENV = .venv
BIN=$(VENV)/bin
PROJECT = library

# make it work on windows too
ifeq ($(OS), Windows_NT)
	BIN=$(VENV)/Scripts
	PYTHON=python
endif

$(VENV): requirements.txt
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade -r requirements.txt

.PHONY: test
test: $(VENV)
	$(BIN)/pytest

.PHONY: start
start: $(VENV)
	$(BIN)/python $(PROJECT)/manage.py runserver

clean:
	rm -rf $(VENV)
	find ./ -type d  \( -name '__pycache__' -or -name '.pytest_cache'  \) -print0 | xargs -tr0 rm -r
