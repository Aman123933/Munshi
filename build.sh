#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "=== 1. Building Frontend SPA ==="
cd frontend
npm ci || npm install
npm run build
cd ..

echo "=== 2. Copying Dist to Backend Static ==="
rm -rf backend/static
cp -r frontend/dist backend/static

echo "=== 3. Installing Backend Dependencies ==="
cd backend
pip install --upgrade pip
pip install -r requirements.txt
cd ..

echo "=== Build Complete ==="
