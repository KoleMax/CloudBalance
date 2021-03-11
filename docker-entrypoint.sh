#!/bin/bash

case "$1" in
  migrate)
    alembic upgrade head
  ;;
  run_bot)
    alembic upgrade head && python main.py
  ;;
esac