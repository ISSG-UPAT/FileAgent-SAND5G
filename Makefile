VENV_DIR=venvs/test_venv
PYTHON=python3
SHELL := /bin/bash


all: install

# ╔═══════════════════════════════╗
# ║ Virtual Environment Functions ║
# ╚═══════════════════════════════╝

$(VENV_DIR):
	@mkdir -p $(VENV_DIR)
	@echo "*" > $(VENV_DIR)/.gitignore 
	@echo "Created virtual environment directory $(VENV_DIR)"

create-venv: $(VENV_DIR)
	@$(PYTHON) -m venv $(VENV_DIR) 
	@echo "Virtual environment created in $(VENV_DIR)"

clean-venv:
	@rm -rf $(VENV_DIR)
	@echo "Removed virtual environment"

venv-upgrade-pip:  
	@source $(VENV_DIR)/bin/activate && pip install --upgrade pip 


# ╔═══════════════════════════════════════════════╗
# ║ Extra functions for extra packages to install ║
# ╚═══════════════════════════════════════════════╝


install-pack-dev:
	@source $(VENV_DIR)/bin/activate && pip install --editable .

install-req-dev:
	@source $(VENV_DIR)/bin/activate && pip install -e .[dev]
	@echo "Development dependencies installed."

install-req-docs:
	@source $(VENV_DIR)/bin/activate && pip install -e .[docs]
	@echo "Documentation dependencies installed."


install-req-all:
	@source $(VENV_DIR)/bin/activate && pip install -e .[dev,docs]
	@echo "All dependencies installed."


# ╔══════════════════════════════════╗
# ║ All in one create venv and setup ║
# ╚══════════════════════════════════╝


setup-all-dev: create-venv venv-upgrade-pip install-dev
	@echo "All development setup steps completed."


# Install the package in editable mode for development process 
install-dev: 
	@source $(VENV_DIR)/bin/activate && pip install --editable . 

# Install the package in normal mode for usage 
install: 
	@source $(VENV_DIR)/bin/activate && pip install . 



# ╔══════════════════════════════════════════════════════════╗
# ║ Build source distribution and wheel using pyproject.toml ║
# ╚══════════════════════════════════════════════════════════╝



build:
	@source $(VENV_DIR)/bin/activate && python -m build --sdist --wheel
	@echo "Source distribution and wheel built."
	@echo "Build completed."

build-check: 
	@source $(VENV_DIR)/bin/activate && python -m twine check dist/*
	@echo "Source distribution with twine check."
	@echo "Build check completed."



# ╔═══════════════════╗
# ║ Upload Functions  ║
# ╚═══════════════════╝


# 
# NOT YET IMPLEMENTED 
upload:
	@source $(VENV_DIR)/bin/activate  && twine upload dist/*

upload-test:
	@source $(VENV_DIR)/bin/activate  && twine upload -r testpypi dist/*
	@echo "Uploaded to Test PyPI."



# ╔════════════════════╗
# ║ Testing Functions  ║
# ╚════════════════════╝


test:
	@source $(VENV_DIR)/bin/activate && pytest -v --tb=short --disable-warnings --maxfail=1
	@echo "Tests completed."


# ╔═════════════════╗
# ║ Documentations  ║
# ╚═════════════════╝

# Documentation using pdoc
# pdoc is a documentation generator for Python projects
# Directory for the pdoc documentation
PDOC_DIR=docs/pdoc/


# Function to ctreate the pdoc directory 
$(PDOC_DIR):
	@mkdir -p $(PDOC_DIR)
	@echo "Created documentation directory $(PDOC_DIR)"


# Function to create the documentation using pdoc
# Leverages the makefile inside docs/
doc-pdoc: $(PDOC_DIR)
	@echo "Generating documentation using pdoc..."
	@source $(VENV_DIR)/bin/activate && make -C $(PDOC_DIR) create
	@echo "Documentation created using pdoc."

# Function to host the documentation html created by pdoc, using pdoc
# Leverages the makefile inside docs/
doc-pdoc-host:
	@echo "Documentation created and hosted by using pdoc."
	@source $(VENV_DIR)/bin/activate && make -C $(PDOC_DIR) host

# ╔════════════════╗
# ║ Help Function  ║
# ╚════════════════╝


help:
	@echo "Makefile for managing Python package setup, testing, and documentation."
	@echo ""
	@echo "Targets:"
	@echo "  create-venv          Create a virtual environment."
	@echo "  clean-venv           Remove the virtual environment."
	@echo "  venv-upgrade-pip     Upgrade pip in the virtual environment."
	@echo "  install-dev     Install the package in editable mode."
	@echo "  install-pack-dev     Install the package in editable mode (alias)."
	@echo "  install-req-dev      Install development dependencies."
	@echo "  install-req-docs     Install documentation dependencies."
	@echo "  install-req-all      Install all dependencies (dev and docs)."
	@echo "  setup-all-dev        Create venv, upgrade pip, and install all dependencies."
	@echo "  build                Build source distribution and wheel using pyproject.toml."
	@echo "  build-check          Check the build with twine."
	@echo "  upload               Upload to PyPI using twine."
	@echo "  upload-test          Upload to Test PyPI using twine."
	@echo "  test                 Run tests using pytest."
	@echo "  doc-pdoc             Generate documentation using pdoc."
	@echo "  doc-pdoc-host        Host documentation using pdoc."
	@echo "  help                 Show this help message."
	@echo ""
	@echo "Note: Use 'source $(VENV_DIR)/bin/activate' to activate the virtual environment."
	@echo "      Use 'deactivate' to exit the virtual environment."
	@echo ""

.PHONY: create-venv clean-venv venv-upgrade-pip install-dev install-pack-dev install-req-dev install-req-docs install-req-all setup-all-dev build build-check upload upload-test test doc-pdoc doc-pdoc-host help

