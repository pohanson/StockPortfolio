#!/bin/sh
if [ -n "$DATABASE_URL" ]; then
    echo "Running migrations...";
    migrate -path ./internal/db/migrations -database "$DATABASE_URL" -verbose up;
    if [ $? -ne 0 ]; then
        echo "Migration failed!"
        exit 1
    fi
else
    echo "DATABASE_URL is not set. Skipping migrations.";
fi

air --build.poll true
