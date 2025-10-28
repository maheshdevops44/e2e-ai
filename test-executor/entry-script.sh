#!/bin/bash

echo "Starting Test Executor Service"

echo "Enabling pgvector extension"
echo $(PGPASSWORD=$DB_PASSWORD psql -h $DB_ENDPOINT -U $DB_USERNAME -d $DB_DATABASE_NAME -p $DB_PORT -c "CREATE EXTENSION IF NOT EXISTS vector;")

echo "pgvector extension enabled"

echo "-------------------------------------------------"

echo "Checking if pgvector extension is enabled"
echo $(PGPASSWORD=$DB_PASSWORD psql -h $DB_ENDPOINT -U $DB_USERNAME -d $DB_DATABASE_NAME -p $DB_PORT -c "SELECT 1 FROM pg_extension WHERE extname = 'vector';")

echo "pgvector extension enabled"

uvicorn api:app --host 0.0.0.0 --port 8000