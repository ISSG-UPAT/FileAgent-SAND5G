SHELL := /bin/bash 
DEST=.
PYTHON=python3
PACKAGE=fileagent

create: 
	pdoc3 $(PACKAGE) --html -o $(DEST)

clean:
	rm -rf $(DEST)/$(PACKAGE) && rm -rf $(DEST)/html

host: 
	cd $(DEST) && $(PYTHON) -m http.server 8500
