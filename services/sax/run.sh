#!/bin/sh

gunicorn --workers=4 --access-logfile=- sax:app -b 0.0.0.0:8165 --timeout=300