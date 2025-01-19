"""
Test custom Django management commands.
"""
from unittest.mock import patch

import psycopg2

from django.core.management import call_command
import django.db.utils
from django.test import SimpleTestCase


@patch("core.management.commands.wait_for_db.Command.check")
class CommandTests(SimpleTestCase):
    def test_wait_for_db_ready(self, patched_check):
        patched_check.return_value = True

        result = call_command("wait_for_db")

        patched_check.assert_called_once_with(databases=["default"])
        self.assertEqual(result, 0)

    @patch("time.sleep")
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        patched_check.side_effect = \
                [psycopg2.OperationalError] * 2 + \
                [django.db.utils.OperationalError] * 3 + \
                [True]

        result = call_command("wait_for_db")

        self.assertEqual(patched_check.call_count, 6)
        self.assertEqual(patched_sleep.call_count, 5)
        patched_check.assert_called_with(databases=["default"])
        self.assertEqual(result, 0)
