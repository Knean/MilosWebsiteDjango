web: daphne milosSite.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: celery -A milosSite  worker -l info



