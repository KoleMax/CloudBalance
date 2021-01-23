#!/bin/bash

case "$1" in
  migrate)
    alembic upgrade head
  ;;
  run_bot)
    python main.py
  ;;
esac