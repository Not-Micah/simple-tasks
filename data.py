import sqlite3
import datetime

months = {1: "Jan", 2:"Feb", 3:"Mar", 4:"Apr", 5:"May", 6:"Jun", 7:"Jul", 8:"Aug", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec"}
days = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}

def load_tasks():
    connection = sqlite3.connect('tasks.db')
    cursor = connection.cursor()

    tasks = []
    for row in cursor.execute("select * from tasks order by due_date"):
        tasks.append(list(row))

    connection.close()
    return tasks

def easy_date(date):
    difference = difference_days(date)

    if difference < 7:
        if difference == 1:
            return "[color=#FFA213]📅 Tomorrow[color=#FFA213]"
        if difference == 0:
            return "[color=#FF0000]🚨 Today[color=#FF0000]"
        return f"[color=#B2B2B2] {difference} Days Left[color=#B2B2B2]"

    someday = datetime.date(int(date[0:4]), int(date[5:7]), int(date[8:10]))
    translation = f"{days.get(someday.weekday())} {date[8:10]}"                     # first part is the day, second part is the date

    if date[5] == "0":                                                              # handling the months -- 1-9 has a 0 infront...
        translation += f" {months.get(int(date[6]))}"
    else:
        translation += f" {months.get(int(date[5:7]))}"

    return f"[color=#b2b2b2]{translation}[color=#b2b2b2]"

def load_quick_tasks():
    connection = sqlite3.connect('tasks.db')
    cursor = connection.cursor()

    quick_tasks = []
    for row in cursor.execute("select * from quick order by completed"):
        quick_tasks.append(list(row))

    connection.close()
    return quick_tasks

def difference_days(date):
    today = datetime.date.today()
    someday = datetime.date(int(date[0:4]), int(date[5:7]), int(date[8:10]))
    differenece = someday - today
    return differenece.days


'''HOW TO TRAIN BASIC DATA SET'''
# connection = sqlite3.connect('tasks.db')
# cursor = connection.cursor()


# cursor.execute("create table if not exists tasks (task_name text, due_date timestamp, description text, completed boolean)")
# task_list = [
#     ("Maths Homework", datetime.date(2021, 12, 25), "Assignment 3", True),
#     ("English Reading", datetime.date(2022, 12, 1), "Read pages 30 - 50", False),
#     ("History Research", datetime.date(2021, 12, 21), "Topic: Impact of TOV on Germany", True),
#     ("Game Coding", datetime.date(2021, 12, 13), "Work on player sprites", False)
# ]
# cursor.executemany("insert into tasks values (?, ?, ?, ?)", task_list)

# cursor.execute("create table if not exists quick (data text, completed boolean)")
# cursor.execute("""
#                 insert into quick (data, completed)
#                 values
#                 ('This is a quick todo!', True)
#                 """)

# connection.commit()
# connection.close()

'''HOW TO EDIT A SPECIFIC ROW IN A DATA SET'''
# cursor.execute("update tasks set task_name=? where task_name=?", ("Cook Dinner", "Game Coding"))