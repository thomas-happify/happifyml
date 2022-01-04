# Makefile
.PHONY: help
help:
	@echo "Commands:"
	@echo "style  : runs style formatting."
	@echo "clean  : cleans all unecessary files."
	@echo "dvc    : pushes versioned artifacts to blob storage."
	@echo "test   : run non-training tests."

# Styling
.PHONY: style
style:
	black .
	flake8
	isort .

# Cleaning
.PHONY: clean
clean:
	find . -type f -name "*.DS_Store" -ls -delete
	find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf
	find . | grep -E ".pytest_cache" | xargs rm -rf
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf
	rm -f .coverage
	rm -f coverage.xml
