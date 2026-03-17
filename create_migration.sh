#!/bin/bash
if [ -z "$1" ]; then
    echo "Usage: ./create_migration.sh 'migration message'"
    exit 1
fi
docker-compose exec web alembic revision --autogenerate -m "$1"