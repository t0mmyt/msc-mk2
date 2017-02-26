#!/bin/sh

gunicorn -w1 --access-logfile=- interface:app -b 0.0.0.0:8180