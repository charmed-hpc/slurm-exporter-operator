SLURM_EXPORTER=slurm-exporter.tar.gz

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: version
version: ## Create/update version file
	@git describe --dirty --tags --always > version

.PHONY: clean
clean: ## Remove build dirs, temp files, and charms
	rm -rf venv/
	rm -rf build
	rm -rf .tox/
	find . -name "*.charm" -delete
	rm -f version

.PHONY: deepclean
deepclean: clean ## Cleanup charmcraft LXD project and charm resources
	@charmcraft clean
	rm ${SLURM_EXPORTER}

.PHONY: resources ## Download resources needed
resources: ${SLURM_EXPORTER}

${SLURM_EXPORTER}: ## Build slurm-exporter tarball
	./scripts/create_tarball.sh

.PHONY: charm
charm: version resources ## Pack the charm
	@charmcraft pack

.PHONY: lint
lint: ## Run linter
	tox -e lint
