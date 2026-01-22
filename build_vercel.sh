#!/bin/bash

# Install Node.js dependencies for Tailwind CSS
npm install

# Build Tailwind CSS
npm run build:css:prod

# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate --noinput
