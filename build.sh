#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install

# Build Tailwind CSS
npm run build:css:prod

# Collect static files
python manage.py collectstatic --noinput

# Removed: python manage.py migrate