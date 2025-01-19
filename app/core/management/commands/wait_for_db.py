"""
Django command to wait for database to be available
"""

import time
import psycopg2
from django.core.management.base import BaseCommand
import django.db.utils


class Command(BaseCommand):
    """Django command to wait for database"""

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")

        db_up = False
        while not db_up:
            try:
                self.check(databases=['default'])
                db_up = True
            except (
                    psycopg2.OperationalError,
                    django.db.utils.OperationalError
            ):
                self.stdout.write("Waiting...")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Database is ready"))
        return 0
