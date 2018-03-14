from collections import OrderedDict
import datetime
import os

from task import Task, DATABASE


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([Task], safe=True)


def menu_loop(message=None):
    """Show the main menu."""
    if not message:
        message = ""
    while True:
        # Main menu input loop
        menu_input = main_menu(message).lower()
        while True:
            if menu_input in menu:
                break
            else:
                menu_input = main_menu("Selection not recognized. Try again.")

        # Runs selected function
        menu[menu_input]()

        # Quit program if selection is q
        if menu_input == 'q':
            break


def main_menu(message=None):
    """
    Runs the main menu.

    Takes one argument 'message' to allow control over a potential
    error message.  Shows a default message if none is provided.

    Returns the user selection from the main menu.
    """
    clear()
    print("WORK LOG\n========\n")
    if message:
        print(message+"\n")
    else:
        print("What would you like to do?\n")
    print("(A)dd a task")
    print("(V)iew all tasks")
    print("(S)earch for a task")
    print("(Q)uit")
    return input("> ")


def clear():
    # os.system('cls' if os.name == 'nt' else 'clear')
    pass


def add_task():
    """Add a task"""
    employee = get_employee()
    duration = get_duration()
    title = get_title()
    notes = get_notes()
    Task.create(employee=employee,
                duration=duration,
                title=title,
                notes=notes)
    input("Task created!  Press Enter to return to main menu.\n")


def get_employee():
    message = ""
    while True:
        clear()
        employee = input(
            "{}Which employee completed the task?\n> ".format(message))
        if len(employee) > 60:
            message = "Name must be 60 or fewer characters.\n\n"
            continue
        return employee


def get_duration():
    message = ""
    while True:
        clear()
        duration = input(
            "{}How long did it take to complete the task? "
            "(in minutes)\n> ".format(message))
        try:
            duration = int(duration)
            if duration < 1:
                raise ValueError
        except ValueError:
            message = "Duration must be a positive whole number.\n\n"
        else:
            return duration


def get_title():
    message = ""
    while True:
        clear()
        title = input(
            "{}Enter a short description of the task:\n> ".format(message))
        if len(title) > 140:
            message = "Task title must be 140 or fewer characters.\n\n"
            continue
        return title


def get_notes():
    clear()
    return input(
        "Enter any additional notes related to the task (optional)\n> ")


def get_date(message=None):
    if not message:
        message = ""
    while True:
        clear()
        date_string = input(
            "{}When was the task completed? (MM/DD/YYYY)\n> ".format(message))
        try:
            date = datetime.datetime.strptime(date_string, "%m/%d/%Y")
        except ValueError:
            message = "Couldn't convert input into date. Try again.\n\n"
            continue
        else:
            return date


def view_all_tasks():
    """View all tasks"""
    tasks = Task.select()
    task_page_menu(tasks)


def search_tasks():
    """Search for a task"""
    search_menu = OrderedDict([
        ('e', employee_search),
        ('t', duration_search),
        ('k', keyword_search),
        ('d', date_search),
        ('r', date_range_search),
    ])
    message = "Enter criteria below:"
    while True:
        clear()
        print("What criteria would you like to use for searching?\n")
        print("Search by (E)mployee name")
        print("Search by Dura(t)ion")
        print("Search by (K)eyword")
        print("Search by (D)ate")
        print("Search by Date (R)ange")
        print("Or go (B)ack")
        print("\n{}\n".format(message))
        choice = input("> ").lower().strip()

        if choice not in ['e', 't', 'k', 'd', 'r', 'b']:
            message = "Entry not recognized. Try again."
            continue
        if choice == 'b':
            break
        tasks = search_menu[choice]()
        if len(tasks) == 0:
            message = "No tasks found by that criteria. Try again."
            continue
        task_page_menu(tasks)


def employee_search():
    message = ""
    while True:
        clear()
        print("Search through employees by:")
        print("  Picking from a (L)ist of employees")
        print("  (E)ntering an employee's name")
        print("\n{}".format(message))
        choice = input("> ").lower().strip()
        print(choice)
        if choice not in ['l', 'e']:
            message = "Entry not recognized. Try again."
            continue
        if choice == 'l':
            return list_of_employees()
        if choice == 'e':
            return employee_by_entry()


def list_of_employees():
    employees = []
    for task in Task.select(Task.employee).distinct():
        employees.append(task.employee)
    message = "Which employee's tasks do you want to view?"
    return employee_from_selection(employees, message)


def employee_by_entry():
    employee = get_employee()
    emp_match = (Task.select(Task.employee)
                 .distinct()
                 .where(Task.employee ** "%{}%".format(employee)))
    if len(emp_match) > 1:
        employees = []
        for emp in emp_match:
            employees.append(emp.employee)
        message = "Multiple employees found with similar name."
        return employee_from_selection(employees, message)
    else:
        if len(emp_match) == 0:
            return []
        employee = emp_match[0].employee
        return Task.select().where(Task.employee == employee)


def employee_from_selection(employees, message):
    error = "====="
    while True:
        clear()
        print("{}\n".format(message))
        for i, emp in enumerate(employees):
            print("({}) {}".format(i, emp))
        print("\n{}\n".format(error))
        employee_index = input("> ")
        try:
            employee_index = int(employee_index)
            if (employee_index < 0 or
                    employee_index > len(employees) - 1):
                raise ValueError
        except ValueError:
            error = "Entry not recognized. Try again."
            continue
        employee = employees[employee_index]
        return Task.select().where(Task.employee == employee)


def duration_search():
    duration = get_duration()
    return Task.select().where(Task.duration == duration)


def keyword_search():
    clear()
    keyword = input("What keyword would you like to search by?\n> ")
    return Task.select().where(Task.title.contains(keyword) |
                               Task.notes.contains(keyword))


def date_search():
    clear()
    start_date = get_date()
    end_date = datetime.datetime.combine(start_date.date(),
                                         datetime.time(23, 59, 59))
    return Task.select().where(Task.created_at.between(start_date, end_date))


def date_range_search():
    start_date = get_date("Enter the beginning date in the date range.\n\n")
    end_date = get_date("Enter the end date in the date range.\n\n")
    return Task.select().where(Task.created_at.between(start_date, end_date))


def task_page_menu(tasks):
    index = 0
    message = "What would you like to do?"
    while True:
        clear()
        task = tasks[index]
        print("TASK\n====\n")
        print("Task ID# {}".format(task.id))
        print("Employee: {}".format(task.employee))
        print("Title: {}".format(task.title))
        print("Duration: {}".format(task.duration))
        print("Notes: {}".format(task.notes))
        print("Date Created: {}".format(task.created_at.strftime("%m/%d/%Y")))
        print("\n{}\n".format(message))

        # Generate valid options and messaging based on current index
        if len(tasks) == 1:
            options = ['e', 'd']
            print("(E)dit, (D)elete,")
        elif index == 0:
            options = ['e', 'd', 'n']
            print("(E)dit, (D)elete, view (N)ext,")
        elif index == len(tasks) - 1:
            options = ['e', 'd', 'p']
            print("(E)dit, (D)elete, view (P)revious,")
        else:
            options = ['e', 'd', 'n', 'p']
            print("(E)dit, (D)elete, view (N)ext, view (P)revious,")
        print("Or go (B)ack.")
        options.append('b')

        # Filter user input
        choice = input("> ").lower()
        if choice not in options:
            message = "Choice not recognized. Try again."
            continue
        if choice == 'e':
            edit_task(task.id)
        if choice == 'd':
            delete_task(task.id)
        if choice == 'n':
            index += 1
            continue
        if choice == 'p':
            index -= 1
            continue
        break


def edit_task(task_id):
    message = "What do you want to update?"
    update = {}
    # Edit input loop
    while True:
        clear()
        print("{}\n".format(message))
        print("(E)mployee")
        print("D(u)ration")
        print("(T)itle")
        print("(N)otes")
        print("(D)ate\n")
        print("Or go (B)ack.")
        field = input("> ").lower()
        if field not in ['e', 'u', 't', 'n', 'd', 'b']:
            message = "Choice not recognized. Try again."
            continue
        if field == 'e':
            update['employee'] = get_employee()
        if field == 'u':
            update['duration'] = get_duration()
        if field == 't':
            update['title'] = get_title()
        if field == 'n':
            update['notes'] = get_notes()
        if field == 'd':
            update['created_at'] = get_date()
        break

    Task.set_by_id(task_id, update)
    input("Task has been updated. Press Enter to return to the main menu.")


def delete_task(task_id):
    if input("Are you sure? [yN] ").lower() == 'y':
        Task.delete_by_id(task_id)
        input("Entry deleted! Press Enter to return to the main menu.")


def quit_program():
    clear()
    print("Thanks for using the work log!\n")


menu = OrderedDict([
    ('a', add_task),
    ('v', view_all_tasks),
    ('s', search_tasks),
    ('q', quit_program),
])


if __name__ == '__main__':
    initialize()
    menu_loop()
