#!/bin/bash
echo 'starting gnicorn now'
gunicorn -w 1 -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -b 0.0.0.0:$PORT --timeout 36000 --forwarded-allow-ips="*" --log-level=info --error-logfile - --access-logfile - chatup_chat.chat:app
