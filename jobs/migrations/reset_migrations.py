#!/usr/bin/env python
import os
import sys
import django
from django.core.management import execute_from_command_line

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greentara.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Delete all migration records
    cursor.execute("DELETE FROM django_migrations WHERE app = 'jobs';")
    print("Reset jobs migration history")

print("Now run: python manage.py makemigrations && python manage.py migrate")