web: gunicorn milosSite.wsgi --log-file -
worker: celery -A milosSite  worker -l info