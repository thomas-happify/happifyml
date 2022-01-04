# Makefile
.PHONY: help
help:
	@echo "Commands:"
	@echo "style  : runs style formatting."
	@echo "clean  : cleans all unecessary files."
	@echo "test   : run non-training tests."

# Styling
.PHONY: style
style:
	pre-commit run -a


# Cleaning
.PHONY: clean
clean:
	find . -type f -name "*.DS_Store" -ls -delete
	find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf
	find . | grep -E ".pytest_cache" | xargs rm -rf
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf
	rm -f .coverage
	rm -f coverage.xml

# Test
.PHONY: test
test: clean
	coverage run -m pytest tests
	coverage report -m
