#!/bin/sh

gunicorn --workers=4 --access-logfile=- tsdatastore:app -b 0.0.0.0:8163 --timeout=300