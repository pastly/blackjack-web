#!/usr/bin/env bash
source bj-venv/bin/activate
source extra-environment
FLASK_APP=application.py flask run
