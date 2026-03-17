#!/bin/bash

echo "Applying migrations..."
docker-compose exec web alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Migrations applied successfully!"
else
    echo "❌ Failed to apply migrations"
    exit 1
fi