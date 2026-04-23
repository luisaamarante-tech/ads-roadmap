#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

workers = os.environ.get("GUNICORN_WORKERS", 2)
threads = os.environ.get("GUNICORN_THREADS", 4)
proc_name = "roadmap"
default_proc_name = proc_name
timeout = 120
bind = "0.0.0.0:8080"
max_requests=10000
max_requests_jitter=2000
capture_output=True
errorlog='-'

# vim: nu ts=4 fdm=indent noet ft=python:
