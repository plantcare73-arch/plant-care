"""
Production Gunicorn Configuration for AI Plant Care System.
Optimized for low-RAM cloud hosting and multi-threaded ML inference.
"""
import os
import multiprocessing

# Network Binding: dynamically bind to $PORT (Render, Cloud Run, Heroku) or default to 5000
port = os.environ.get("PORT", "5000")
bind = f"0.0.0.0:{port}"
backlog = 2048

# Concurrency & Worker Model
# 2 workers with 4 threads each gives 8 concurrent request slots.
# Preload loads the TensorFlow/Keras model ONCE in master process before forking,
# cutting RAM usage from ~1.5GB down to ~520MB across workers via Copy-On-Write.
workers = 2
threads = 4
worker_class = "gthread"
preload_app = True

# Timeouts & Keepalive
# 120s accommodates image upload, preprocessing, and model inference on cold requests
timeout = 120
keepalive = 5

# Security Limits
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
max_requests = 1000
max_requests_jitter = 50

# Logging Configuration
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)sµs'
