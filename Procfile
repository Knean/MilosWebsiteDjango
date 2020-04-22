web: daphne milosSite.asgi:channel_layer --port $PORT --bind 0.0.0.0 -v2
worker: celery -A milosSite  worker -l info

