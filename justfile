# Cargar variables desde el archivo .env si existe
set dotenv-load := true

export APP_DIR := file_name(invocation_directory())
export PARENT_DIR := "taller"

# Comando por defecto
default:
    @just --list
# para construir el paquete
build:
    uv build

# para publicar el paquete en PyPI
publish:
    uv publish

# Run the test suite with verbose output using pytest
test:
	uv run --active pytest -v  --showlocals

# Run all code quality checks (formatting and linting)
check: format-check lint-check
# Check code formatting compliance without making changes
format-check:
	uv run ruff format --check .
# Run linting checks to identify code quality issues without fixing
lint-check:
	uv run ruff check .
# Fix code quality issues automatically
fix: format lint
# Automatically format code according to ruff rules
format:
	uv run ruff format .
# Run linting checks and automatically fix issues where possible  
lint:
	uv run ruff check --fix .
# Generate a changelog from git commit history using git-chglog Output is saved to CHANGELOG.md
changelog:
	uv run gitchangelog > CHANGELOG.md

# Sincronizar con rclone, hacer commit y push a GitHub
push:
    #!/usr/bin/env bash

    # Detener el script si un comando falla
    set -e  

    rclone sync . gd-ricardo:{{PARENT_DIR}}/{{APP_DIR}} --exclude-from ./rcloneignore.txt --progress -v 

    read -p "Mensaje de commit (Required): " req

    if [ -z "$req" ]; then 
        echo "Error: El mensaje requerido no puede estar vacío."
        exit 1
    fi

    read -p "Descripción adicional (Optional): " opt

    git add .

    if [ -z "$opt" ]; then
        git commit -m "$req"
    else
        git commit -m "$req" -m "$opt"
    fi

    git push
