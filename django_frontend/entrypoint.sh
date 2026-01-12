#!/bin/bash

# 데이터베이스 마이그레이션 실행
echo "Running database migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Django 개발 서버 실행
echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000
