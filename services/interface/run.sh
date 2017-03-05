#!/bin/sh

gunicorn --workers=4 --access-logfile=- interface:app -b 0.0.0.0:8180  --timeout=600