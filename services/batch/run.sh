#!/bin/sh

celery -A batch.tasks worker --loglevel=info