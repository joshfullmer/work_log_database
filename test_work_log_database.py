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

        self.long_employee = ("TestMcTestersonTestMcTestersonTestMcTesterson"
                              "TestMcTestersonTestMcTestersonTestMcTesterson")
        self.long_title = ("TestTaskTitleTestTaskTitleTestTaskTitleTestTaskTi"
                           "TestTaskTitleTestTaskTitleTestTaskTitleTestTaskTi"
                           "TestTaskTitleTestTaskTitleTestTaskTitleTestTaskTi"
                           "TestTaskTitleTestTaskTitleTestTaskTitleTestTaskTi"
                           "TestTaskTitleTestTaskTitleTestTaskTitleTestTaskTi")

    def test_db_initiate(self):
        DATABASE.close()
        work_log_database.initialize()
        self.assertTrue(os.path.isfile('work_log.db'))

    @patch('builtins.input', return_value='q')
    def test_main_menu_exit(self, mock):
        work_log_database.menu_loop()

    @patch('builtins.input', side_effect=['x', 'q'])
    def test_main_menu_error(self, mock):
        work_log_database.menu_loop()

    @patch('builtins.input', side_effect=['v', 'b', 'q'])
    def test_view_all_tasks(self, mock):
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

    @patch('builtins.input')
    def test_employee_validation(self, mock):
        mock.side_effect = [self.long_employee, self.employee]
        self.assertEqual(work_log_database.get_employee(), self.employee)

    @patch('builtins.input')
    def test_duration_validation(self, mock):
        mock.side_effect = ["-15", self.duration]
        self.assertEqual(work_log_database.get_duration(), self.duration)

    @patch('builtins.input')
    def test_title_validation(self, mock):
        mock.side_effect = [self.long_title, self.title]
        self.assertEqual(work_log_database.get_title(), self.title)

    @patch('builtins.input')
    def test_date_validation(self, mock):
        date = "01/01/2018"
        parsed_date = datetime.datetime.strptime(date, "%m/%d/%Y")
        mock.side_effect = ["13/12/2018", date]
        self.assertEqual(work_log_database.get_date(), parsed_date)


if __name__ == '__main__':
    unittest.main()
