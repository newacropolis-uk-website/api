.DEFAULT_GOAL := help
SHELL := /bin/bash

.PHONY: help
help:
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: test
test: ## Run all tests
	./scripts/run_tests.sh

.PHONY: test-one
test-one: ## Test one, make test-one test=<test function name>
	pytest -k ${test}

.PHONY: test-dir
test-dir: ## Test directory under tests/app, make test-dir dir=<directory of tests>
	pytest tests/app/${dir}
