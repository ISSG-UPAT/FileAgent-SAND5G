SHELL := /bin/bash 
DEST=.
PYTHON=python3
PACKAGE=fileagent

create: 
	pdoc3 $(PACKAGE) --html -o $(DEST)

host: 
	cd $(DEST) && $(PYTHON) -m http.server 8500
