VENV_DIR=venvs/test_venv
PYTHON=python3
SHELL := /bin/bash


all: setup-all-dev

setup-toml: 
	@source $(VENV_DIR)/bin/activate && pip install --editable . 


# Virtual environment functions 

create-venv:
	@$(PYTHON) -m venv $(VENV_DIR) 
	@echo "Virtual environment created in $(VENV_DIR)"

clean-venv:
	@rm -rf $(VENV_DIR)
	@echo "Removed virtual environment"

venv-upgrade-pip:  
	@source $(VENV_DIR)/bin/activate && pip install --upgrade pip 


# Extra functions for extra packages to install 


install-pack-dev:
	@source $(VENV_DIR)/bin/activate && pip install --editable .

install-req-dev:
	@source $(VENV_DIR)/bin/activate && pip install -e .[dev]
	@echo "Development dependencies installed."

install-req-docs:
	@source $(VENV_DIR)/bin/activate && pip install -e .[docs]
	@echo "Documentation dependencies installed."


# All in one create venv and setup 

setup-all-dev: create-venv venv-upgrade-pip setup-toml install-req-dev install-req-docs
	@echo "All development setup steps completed."


# Upload to py
# NOT YET IMPLEMENTED 
upload-pypi:
	@source $(VENV_DIR)/bin/activate  && twine upload dist/*


# Documentation 

PDOC_DIR=docs/pdoc/

$(PDOC_DIR):
	@mkdir -p $(PDOC_DIR)
	@echo "Created documentation directory $(PDOC_DIR)"


doc-pdoc: $(PDOC_DIR)
	@echo "Generating documentation using pdoc..."
	@source $(VENV_DIR)/bin/activate && make -C $(PDOC_DIR) create
	@echo "Documentation created using pdoc."


doc-pdoc-host:
	@echo "Documentation created and hosted by using pdoc."
	@source $(VENV_DIR)/bin/activate && make -C $(PDOC_DIR) host


help:
	@echo "Makefile for managing Python package setup and documentation."
	@echo ""
	@echo "Targets:"
	@echo "  create-venv        Create a virtual environment."
	@echo "  clean-venv         Remove the virtual environment."
	@echo "  venv-upgrade-pip   Upgrade pip in the virtual environment."
	@echo "  setup-toml         Build source distribution and wheel using pyproject.toml."
	@echo "  install-pack-dev   Install the package in editable mode."
	@echo "  install-req-dev    Install development dependencies."
	@echo "  install-req-docs   Install documentation dependencies."
	@echo "  setup-all-dev      Create venv, upgrade pip, and install all dependencies."
	@echo "  upload-pypi       Upload to PyPI using twine."
	@echo "  doc-pdoc          Generate documentation using pdoc."
	@echo "  doc-pdoc-host     Host documentation using pdoc."
	@echo "  help              Show this help message."
	@echo ""
	@echo "Note: Use 'source $(VENV_DIR)/bin/activate' to activate the virtual environment."
	@echo "      Use 'deactivate' to exit the virtual environment."
	@echo ""
	@echo "Makefile for managing Python package setup and documentation."


.PHONY: create-venv clean-venv venv-upgrade-pip setup-toml install-pack-dev install-req-dev install-req-docs setup-all-dev upload-pypi doc-pdoc doc-pdoc-host help
