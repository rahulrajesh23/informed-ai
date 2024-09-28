.PHONY: install
install: ## 🚀 Install the poetry environment and install the pre-commit hooks
	@echo "🎉 Creating virtual environment using pyenv and poetry"
	@poetry install
	@poetry shell

.PHONY: build-pgvector
build-pgvector:
	@eval $$(minikube docker-env) ;\
	echo "📦 Building cleric-pgvector" && \
	docker build misc/images/pgvector -t gcr.io/informed/informed-pgvector:latest


.PHONY: build-pgvector-local
build-pgvector-local:
	docker build misc/images/pgvector -t gcr.io/informed/informed-pgvector:latest


.PHONY: local-db
local-db: build-pgvector-local
	docker run -d \
		-p 5432:5432 \
		-e POSTGRESQL_USERNAME=test \
		-e POSTGRESQL_PASSWORD=test \
		-e POSTGRESQL_DATABASE=test \
		-e POSTGRES_POSTGRES_PASSWORD=password \
		-e POSTGRES_INITSCRIPTS_USERNAME=postgres \
		-e POSTGRES_INITSCRIPTS_PASSWORD=password \
		--name informed-postgres \
		gcr.io/informed/informed-pgvector:latest

.PHONY: destroy-local-db
destroy-local-db:
	@docker stop informed-postgres || true
	@docker rm informed-postgres || true

.PHONY: dev.migration.create
dev.migration.create: build-pgvector-local
	@poetry run python misc/scripts/create_migration.py -m "$m"