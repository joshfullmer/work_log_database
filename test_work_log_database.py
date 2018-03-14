import datetime
import os
import unittest
from unittest.mock import patch

from task import Task, DATABASE
import work_log_database


class TaskTests(unittest.TestCase):

    def test_task_create(self):
        employee = "Test McTesterson"
        duration = 15
        title = "Test Task Title"
        notes = "Test Notes"

        Task.create(employee=employee,
                    duration=duration,
                    title=title,
                    notes=notes)
        latest = Task.select().order_by(Task.id.desc()).get()
        self.assertEqual(employee, latest.employee)
        self.assertEqual(duration, latest.duration)
        self.assertEqual(title, latest.title)
        self.assertEqual(notes, latest.notes)
        self.assertEqual(datetime.date.today(), latest.created_at.date())
        Task.delete_by_id(latest.id)


class WorkLogTests(unittest.TestCase):

    def setUp(self):
        self.employee = "Test McTesterson"
        self.duration = 15
        self.title = "Test Task Title"
        self.notes = "Test Notes"

    def test_db_initiate(self):
        DATABASE.close()
        work_log_database.initialize()
        self.assertTrue(os.path.isfile('work_log.db'))

    @patch('builtins.input', return_value='q')
    def test_main_menu_exit(self, input):
        work_log_database.menu_loop()

    @patch('builtins.input', side_effect=['x', 'q'])
    def test_main_menu_error(self, input):
        work_log_database.menu_loop()

    @patch('builtins.input')
    def test_add_task_menu(self, mock):
        mock.side_effect = [
            self.employee,
            str(self.duration),
            self.title,
            self.notes,
            ''
        ]
        work_log_database.add_task()
        latest = Task.select().order_by(Task.id.desc()).get()
        self.assertEqual(self.employee, latest.employee)
        self.assertEqual(self.duration, latest.duration)
        self.assertEqual(self.title, latest.title)
        self.assertEqual(self.notes, latest.notes)
        self.assertEqual(datetime.date.today(), latest.created_at.date())

if __name__ == '__main__':
    unittest.main()
