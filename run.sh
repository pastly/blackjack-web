#!/usr/bin/env bash
source bj-venv/bin/activate
source extra-environment
FLASK_APP=application.py flask run --host 0.0.0.0
