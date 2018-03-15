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
        self.similar_employee = "Testy Dude"

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

    @patch('builtins.input', side_effect=['e', 'l', '0', 'b', 'b'])
    def test_search_menu(self, mock):
        work_log_database.search_tasks()

    @patch('builtins.input', side_effect=['x', 'b'])
    def test_search_menu_error(self, mock):
        work_log_database.search_tasks()

    @patch('builtins.input', side_effect=['k', 'defenestration', 'b'])
    def test_search_menu_no_tasks(self, mock):
        work_log_database.search_tasks()

    @patch('builtins.input', side_effect=['e', 'x', 'l', '0', 'b', 'b'])
    def test_employee_search_missing(self, mock):
        work_log_database.search_tasks()

    @patch('builtins.input')
    def test_employee_entry(self, mock):
        mock.side_effect = ['e', self.employee, 'b', 'b']
        work_log_database.employee_search()

    @patch('builtins.input')
    def test_employee_entry_gt_one(self, mock):
        mock.side_effect = [
            'e',
            'test',
            '0',
            'b',
            'b',
        ]
        Task.create(
            employee=self.similar_employee,
            duration=self.duration,
            title=self.title,
            notes=self.notes,
        )
        work_log_database.employee_search()

    @patch('builtins.input')
    def test_employee_entry_empty(self, mock):
        mock.side_effect = ['e', 'defenestration', 'b']
        work_log_database.employee_search()

    @patch('builtins.input', side_effect=['-1', '0'])
    def test_employee_entry_invalid_index(self, mock):
        employees = ['Test', 'Tester']
        work_log_database.employee_from_selection(employees, '')

    @patch('builtins.input', return_value='10')
    def test_duration_search(self, mock):
        work_log_database.duration_search()

    @patch('builtins.input', return_value='12/12/2018')
    def test_date_search(self, mock):
        work_log_database.date_search()

    @patch('builtins.input', side_effect=['01/01/2018', '12/12/2018'])
    def test_date_range_search(self, mock):
        work_log_database.date_range_search()

    @patch('builtins.input', side_effect=['x', 'e', 'x', 'e', 'Doc Brown', ''])
    def test_task_page_single(self, mock):
        Task.create(
            employee='Marty Mcfly',
            duration=88,
            title='Back in Time',
            notes='Power of Love',
        )
        tasks = Task.select().where(Task.employee == 'Marty Mcfly')
        work_log_database.task_page_menu(tasks)
        Task.delete_by_id(tasks[0].id)

    @patch('builtins.input', side_effect=['d', 'y', ''])
    def test_task_page_delete(self, mock):
        Task.create(
            employee='Peter Parker',
            duration=8,
            title='Spiderman',
            notes='Amazing',
        )
        tasks = Task.select().where(Task.employee == 'Peter Parker')
        work_log_database.task_page_menu(tasks)

    @patch('builtins.input', side_effect=['n', 'n', 'p', 'b'])
    def test_task_page_three(self, mock):
        Task.create(
            employee='Marty Mcfly',
            duration=88,
            title='Back in Time',
            notes='Power of Love',
        )
        Task.create(
            employee='Marty Mcfly',
            duration=88,
            title='Back in Time',
            notes='Power of Love',
        )
        Task.create(
            employee='Marty Mcfly',
            duration=88,
            title='Back in Time',
            notes='Power of Love',
        )
        tasks = Task.select().where(Task.employee == 'Marty Mcfly')
        work_log_database.task_page_menu(tasks)
        for task in tasks:
            Task.delete_by_id(task.id)

    @patch('builtins.input', side_effect=['u', '30', ''])
    def test_edit_task_duration(self, mock):
        Task.create(
            employee='Peter Parker',
            duration=8,
            title='Spiderman',
            notes='Amazing',
        )
        tasks = Task.select().where(Task.employee == 'Peter Parker')
        work_log_database.edit_task(tasks[0].id)

    @patch('builtins.input', side_effect=['t', 'Venom', ''])
    def test_edit_task_title(self, mock):
        Task.create(
            employee='Peter Parker',
            duration=8,
            title='Spiderman',
            notes='Amazing',
        )
        tasks = Task.select().where(Task.employee == 'Peter Parker')
        work_log_database.edit_task(tasks[0].id)

    @patch('builtins.input', side_effect=['n', 'The Amazing', ''])
    def test_edit_task_notes(self, mock):
        Task.create(
            employee='Peter Parker',
            duration=8,
            title='Spiderman',
            notes='Amazing',
        )
        tasks = Task.select().where(Task.employee == 'Peter Parker')
        work_log_database.edit_task(tasks[0].id)

    @patch('builtins.input', side_effect=['d', '05/04/2018', ''])
    def test_edit_task_date(self, mock):
        Task.create(
            employee='Peter Parker',
            duration=8,
            title='Spiderman',
            notes='Amazing',
        )
        tasks = Task.select().where(Task.employee == 'Peter Parker')
        work_log_database.edit_task(tasks[0].id)


if __name__ == '__main__':
    unittest.main()
