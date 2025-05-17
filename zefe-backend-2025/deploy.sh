#!/bin/bash

# Stop immediately if a command exits with a non-zero status
set -e

echo "🔄 Pulling latest code from main branch..."
git pull origin main

echo "🐳 Rebuilding Docker containers..."
docker compose build

echo "🚀 Restarting Docker containers..."
docker compose up -d

echo "✅ Deployment complete!"
