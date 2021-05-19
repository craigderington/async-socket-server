source venv/bin/activate
celery -A app:celery worker -l DEBUG -n worker%h -c 2