#!/bin/bash

case "$1" in
  migrate)
    alembic upgrade head
  ;;
  run_bot)
    exec python3 ./application/app.py
  ;;
esac