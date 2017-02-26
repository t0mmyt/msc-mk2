#!/bin/sh

gunicorn --workers=4 --access-logfile=- obsloader:app -b 0.0.0.0:8164  --timeout=300