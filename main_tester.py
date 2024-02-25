from kivymd.uix.card                import MDCard
from kivymd.app                     import MDApp
from kivymd.uix.boxlayout           import MDBoxLayout
from kivymd.uix.dialog              import MDDialog
from kivymd.uix.pickers             import MDDatePicker
##########
import sqlite3
from datetime                       import datetime, date
from data                           import load_tasks, load_quick_tasks, difference_days, easy_date
##########
import calendar
from kivy.uix.label                 import Label
from kivy.uix.button                import Button
##########
from kivymd.uix.floatlayout         import MDFloatLayout
##########
from kivymd.uix.list                import IRightBodyTouch
from kivymd.uix.selectioncontrol    import MDCheckbox
from kivymd.uix.list                import OneLineAvatarIconListItem
##########
from themes                         import color_themes
from kivymd.uix.fitimage            import FitImage
########## TESTING...
from kivy.clock import mainthread, Clock
from threading import Thread
##########
from kivy.animation import Animation
from kivy.graphics import Ellipse, Color
from kivy.properties import NumericProperty
##########
from kivy.properties import BooleanProperty


connection = sqlite3.connect('tasks.db')
cursor = connection.cursor()

with open('bg.txt', 'r') as f:
    bg_choice = f.readline()

''' BACKGROUND SELECTION '''
class BackgroundDialog(MDBoxLayout):
    pass

''' MAIN TASKS '''
class DialogBox(MDBoxLayout):
    pass

class CreateTaskDialog(MDBoxLayout):
    pass

class Card(MDCard):
    pass

''' CALENDAR ITEMS '''
class CircleButton(MDFloatLayout):
    R = NumericProperty(0) 
    G = NumericProperty(0) 
    B = NumericProperty(0)  

    def __init__(self, **kwargs):
        super(CircleButton, self).__init__(**kwargs)
        with self.canvas.before:
            Color(self.R, self.G, self.B)
            self.circle = Ellipse(pos=self.pos, size=(self.width, self.height))

    def on_size(self, *args):
        size = min(self.width, self.height)
        # Set the size to 1/3 of the current size
        new_size = size / 1.5
        self.circle.size = (new_size, new_size)
        self.circle.pos = (
            self.center_x - new_size / 2,
            self.center_y - new_size / 2
        )

class LevitatingCircle(MDFloatLayout):    
    def __init__(self, date, **kwargs):
        super().__init__(**kwargs)
        self.ids.date_button.text = str(date)
        self.ids.date_label.text = str(date)

''' QUICK ITEM TO DO '''
class RightCheckbox(IRightBodyTouch, MDCheckbox):
    pass

class QuickToDoItem(OneLineAvatarIconListItem):
    pass

class CreateQuickToDo(MDBoxLayout):
    pass

class EditQuickToDo(MDBoxLayout):
    pass

''' MAIN CLASS ! '''
class MainApp(MDApp):
    ####
    isready = BooleanProperty(False)
    
    ####
    today = Label(text=date.today().strftime("%d"))     # date as a button for arguments...

    ####
    current_task, current_quick, active_dialog = None, None, None

    ####
    current_month, current_year = date.today().month,date.today().year

    #######################
    bg, accent, status, day_highlight = color_themes[bg_choice]

    #######################
    last_day_pressed = today
    active_page = "Home"
        
    def on_start(self):
        ### removing FitImage Lag
        self.root.ids.image_header.source = self.bg

        ### loading in on_start
        # self.statusbar(self.status)
        Animation(opacity=1, duration=0).start(self.root.ids.app_home)
        self.isready = True
    
    @mainthread
    def on_isready(self, *largs):
        def load_all(*l):            
            # initializing home, calendar and quick tasks
            self.update_tasks()
            self.update_calendar(start=True)
            self.update_quicks()

            # initializing create and edit task dialog
            self.create_task_dialog = MDDialog(title="Task Info", type="custom", content_cls=CreateTaskDialog())
            self.edit_dialog = MDDialog(title="Task Info", type="custom", content_cls=DialogBox())

            # initializing create and edit qt dialog
            self.create_qt_dialog = MDDialog(title="Quick To Do", type="custom", content_cls=CreateQuickToDo())
            self.edit_qt_dialog = MDDialog(title="Quick To Do", type="custom", content_cls=EditQuickToDo())

            # initializing date picker 
            self.date_dialog = MDDatePicker(mode="picker")
            self.date_dialog.bind(on_save=self.change_date)

            # initializing background selector
            def bg_press(x):
                self.active_dialog.dismiss()
                with open('bg.txt', 'w') as f:
                    f.write(x.text)
                
                bg_choice = x.text
                source, md_bg_color, status, day_rgb = color_themes[bg_choice]

                self.root.ids.image_header.source = source
                self.root.ids.task_create.md_bg_color = md_bg_color
                self.root.ids.qt_create_btn.md_bg_color = md_bg_color
                self.day_highlight = day_rgb
                # self.statusbar(status)

                self.update_calendar()

            self.bg_dialog = MDDialog(title="Background Theme", type="custom", content_cls=BackgroundDialog())

            for theme, picture_location in color_themes.items():
                itmg = MDFloatLayout()

                img = FitImage(
                    source=picture_location[0],
                    radius=[15, 15, 15, 15],
                    pos_hint={"center_x": .5, "center_y": .5},
                    size_hint=(1, 1)
                )

                btn = Button(
                    text=theme,
                    background_color=[0, 0, 0, 0],
                    pos_hint={"center_x": .5, "center_y": .5},
                    on_press=bg_press
                )

                itmg.add_widget(btn)
                itmg.add_widget(img)

                self.bg_dialog.content_cls.ids.backgrounds.add_widget(itmg)

        Clock.schedule_once(load_all, .1)

    @mainthread
    def update_tasks(self):
        self.root.ids.container.clear_widgets()
        self.tasks = load_tasks()
        task_count = 0      

        for x in range(len(self.tasks)):
            card = Card()
          
            if difference_days(self.tasks[x][1]) < 0:                   # if the task date is negative, the loop skips
                continue

            card.ids.complete.active = self.tasks[x][3]                 # setting card checkbox
            card.ids.date.name = self.tasks[x][1][0:10]                 # name property to store SQL date
            card.ids.date.text = easy_date(self.tasks[x][1])            # setting card date  
            card.ids.task.text = self.tasks[x][0]                       # setting card title
            task_count += 1
   
            self.root.ids.container.add_widget(card)       

        task_text = "Ongoing Tasks" if task_count != 1 else "Ongoing Task"                                                                                          # handling plural/singular
        self.root.ids.ongoing_task_header.text = f"{date.today().day} {calendar.month_abbr[date.today().month]} {date.today().year}, {task_count} {task_text}"      # day > month > year

    @mainthread
    def update_calendar(self, start=False):
        self.root.ids.calendar_grid.clear_widgets()
        self.tasks = load_tasks()

        # buttons to switch in between months
        if start:                                                           # start (of application)
            self.root.ids.calendar_buttons.clear_widgets()

            for x in range(7):
                if x == 1:
                    # create a button to switch to the previous month
                    button = Button(markup=True, text='[b]<[/b]', size_hint=(0.1, 0.1), background_color=[0,0,0,0], color="22252E")
                    button.bind(on_press=self.prev_month)

                elif x == 3:
                    # create a label to display the current month and year
                    month_name = calendar.month_name[self.current_month]
                    button = Label(markup=True, text=f'[b]{month_name[0:3]} {self.current_year}[/b]', font_size='20sp', color="22252E")

                elif x == 5:
                    # create a button to switch to the next month
                    button = Button(markup=True, text='[b]>[/b]', size_hint=(0.1, 0.1), background_color=[0,0,0,0], color="22252E")
                    button.bind(on_press=self.next_month)

                else:
                    button = Button(text=' ', font_size='20sp', background_color=[0,0,0,0], color="22252E")

                self.root.ids.calendar_buttons.add_widget(button)

            # add labels for the days of the week...
            for day_name in calendar.day_abbr:
                self.root.ids.calendar_buttons.add_widget(Label(text=day_name[0], font_size='15sp', color="22252E"))

        # generate array/string with calendar format...
        month_calendar = calendar.monthcalendar(self.current_year, self.current_month)

        '''
        TO GET DATES WITH TASKS
        '''
        def has_task(day):
            # checking if the date is in the task list
            if f"{self.current_year}-{self.current_month:02}-{day:02}" in [row[1][0:10] for row in self.tasks]:
                return True
            return False

        # add buttons to access different dates...
        four975 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]

        for week in month_calendar:
            for day in week:
                if day == 0:
                    button = Button(text=' ', font_size='20sp', background_color=[0,0,0,0], color="22252E")

                else:
                    # if the date is today
                    if datetime.today().strftime('%Y-%m-%d') == f'{self.current_year}-{self.current_month:02}-{day:02}':
                        button = CircleButton(R=self.day_highlight[0], G=self.day_highlight[1], B=self.day_highlight[2])
                        button.ids.date.text = str(day)
                        button.ids.hidden_button.text = str(day)
                        button.ids.hidden_button.bind(on_press=self.on_day_button_pressed)

                    # if the date has a task
                    elif has_task(day):
                        button = LevitatingCircle(day)
                        button.ids.date_button.bind(on_press=self.on_day_button_pressed)
                    
                    else:
                        button = Button(text=str(day), font_size='15sp', background_color=[0,0,0,0], color="22252E")
                        button.bind(on_press=self.on_day_button_pressed)

                self.root.ids.calendar_grid.add_widget(button)
        
    @mainthread
    def card_specified_update(self, active):
        if active == "Home":
            self.root.ids.date_tasks.clear_widgets()
            self.update_calendar()

        if active == "Calendar":
            self.update_tasks()

    '''BACKGROUND SELECTION'''
    @mainthread
    def open_background_dialog(self):
        self.active_dialog = self.bg_dialog
        self.bg_dialog.open()

    '''QUICK TASK FUNCTIONS'''
    @mainthread
    def update_quicks(self):
        self.root.ids.quick_container.clear_widgets()
        quicks = load_quick_tasks()

        for task_text, task_status in quicks:
            item = QuickToDoItem(text=task_text)
            item.ids.status.active = task_status
            self.root.ids.quick_container.add_widget(item)

    @mainthread
    def open_create_qt_dialog(self):
        self.active_dialog = self.create_qt_dialog
        self.create_qt_dialog.open()

    @mainthread
    def open_edit_qt_dialog(self, title):
        self.edit_qt_dialog.content_cls.ids.task_desc.text = title
        self.active_dialog = self.edit_qt_dialog
        self.edit_qt_dialog.open()

    def create_qt(self, title):
        if title:
            # adding task to SQL db                                                  
            cursor.execute("insert into quick values (?, ?)", [title, False])                                
            connection.commit()

            # closing dialogue and reloading tasks
            self.active_dialog.dismiss()                                                             
            self.update_quicks()

    def save_qt_edits(self, new):
        # saving edited task to SQL db
        cursor.execute("update quick set data=? where data=?", (new, self.current_quick.text))
        connection.commit()
        
        # closing the dialogue and refreshing tasks
        self.active_dialog.dismiss()
        self.update_quicks()

    def delete_qt(self):
        # deleting the task from the SQL
        cursor.execute("delete from quick where data=?", ([self.current_quick.text]))
        connection.commit()

        # closing dialogue and refreshing
        self.active_dialog.dismiss()
        self.update_quicks()

    def save_qt_checkbox(self, quick):
        cursor.execute("update quick set completed=? where data=?", (quick.ids.status.active, quick.text))    
        connection.commit()

    '''CALENDAR FUNCTIONS'''
    @mainthread
    def prev_month(self, instance):
        self.current_month -= 1
        if self.current_month == 0:
            self.current_month = 12
            self.current_year -= 1
        self.update_calendar(start=True)

    @mainthread
    def next_month(self, instance):
        self.current_month += 1
        if self.current_month == 13:
            self.current_month = 1
            self.current_year += 1
        self.update_calendar(start=True)

    def on_day_button_pressed(self, instance):
        self.root.ids.date_tasks.clear_widgets()
        self.last_day_pressed = instance

        day = int(instance.text)
        date = f'{self.current_year}-{self.current_month:02}-{day:02}'

        self.root.ids.bar_date_calendar.text = f'Tasks For {day} {calendar.month_abbr[self.current_month]}, {self.current_year}'

        if date in [row[1][0:10] for row in self.tasks]:
            tasks = load_tasks()

            for row in range(len(tasks)):
                if tasks[row][1][0:10] == date:
                    card = Card()                                                                                   # creating an instance of the the card class
                    user_date = easy_date(self.tasks[row][1]) 

                    card.ids.complete.active = self.tasks[row][3]                                                   # setting the checkbox
                    card.ids.date.name = self.tasks[row][1][0:10]                                                   # creating name to store date
                    card.ids.date.text = user_date                                                                  # setting the date  
                    card.ids.task.text = self.tasks[row][0]                                                         # settings  the  title

                    self.root.ids.date_tasks.add_widget(card)
        else:
            self.root.ids.date_tasks.clear_widgets()

    '''TASK CALENDAR DATE SELECTOR'''
    @mainthread
    def open_date_picker(self):
        self.date_dialog.open()

    @mainthread
    def change_date(self, instance, value, data_range):
        self.active_dialog.content_cls.ids.task_date.text = str(value)
        self.active_dialog.content_cls.ids.task_date.color = "#9f9f9f"

    '''DIALOG / INPUT FUNCTIONS'''
    @mainthread
    def open_create_task_dialog(self):
        self.active_dialog = self.create_task_dialog
        self.create_task_dialog.open()

    def open_edit_task_dialogue(self, task, date):
        task_description = []
        for row in cursor.execute("select description from tasks where task_name=?", ([task])):
             task_description.append(row)

        self.edit_dialog.content_cls.ids.task_text.text = task                           # presetting the task name in the dialogue
        self.edit_dialog.content_cls.ids.task_date.text = date                           # presetting the task date in the dialogue
        self.edit_dialog.content_cls.ids.task_desc.text = task_description[0][0]         # sqlite desc given in a list of tupples

        self.active_dialog = self.edit_dialog
        self.edit_dialog.open()

    def create_task(self):        
        task_date = self.create_task_dialog.content_cls.ids.task_date.text                                          

        if task_date != "Date":                                                             # if the user has already entered a date / default value gone
            task_text = self.create_task_dialog.content_cls.ids.task_text.text
            task_desc = self.create_task_dialog.content_cls.ids.task_desc.text

            # threaded function
            def insert_task():
                thread_connection = sqlite3.connect('tasks.db')
                thread_cursor = thread_connection.cursor()

                thread_cursor.execute("insert into tasks values (?, ?, ?, ?)", [task_text,
                                                                                datetime.strptime(task_date, "%Y-%m-%d"),
                                                                                task_desc,
                                                                                False])
                thread_connection.commit()
                thread_cursor.close()
                thread_connection.close()

                # perform other UI-related operations (outside the thread)
                self.update_tasks()
                self.update_calendar()

            # Create a new thread and start it
            Thread(target=insert_task).start()
            self.create_task_dialog.dismiss() 

        else:                                                                   # if the use has not entered a date yet
            self.active_dialog.content_cls.ids.task_date.color = "#FF9494"      # the date will turn red (notify user)

    def delete_task(self):
        # threaded function
        def delete_task_thread():
            thread_connection = sqlite3.connect('tasks.db')
            thread_cursor = thread_connection.cursor()

            # Execute the update query
            thread_cursor.execute("delete from tasks where task_name=?", [self.current_task.ids.task.text])

            thread_connection.commit()
            thread_cursor.close()
            thread_connection.close()

            # perform UI-related operations (in the main thread using Clock.schedule_once)
            self.update_tasks()
            self.update_calendar()

        Thread(target=delete_task_thread).start()

        self.active_dialog.dismiss()
        self.root.ids.bar_date_calendar.text = "No Date Selected"
        self.root.ids.date_tasks.clear_widgets()

    '''SAVING / DATABASE FUNCTIONS'''
    def save_task_edits(self, task, date):
        task_name = self.current_task.ids.task.text
        task = self.edit_dialog.content_cls.ids.task_text.text
        date = self.edit_dialog.content_cls.ids.task_date.text

        # threaded function
        def update_task_thread():
            thread_connection = sqlite3.connect('tasks.db')
            thread_cursor = thread_connection.cursor()

            thread_cursor.execute("UPDATE tasks SET task_name=?, due_date=?, description=? WHERE task_name=?",
                                (task, datetime.strptime(date, '%Y-%m-%d'), self.edit_dialog.content_cls.ids.task_desc.text, task_name))

            thread_connection.commit()
            thread_cursor.close()
            thread_connection.close()

            # perform UI-related operations (in the main thread using Clock.schedule_once)
            self.update_tasks()
            self.update_calendar()

        # Create a new thread and start it
        Thread(target=update_task_thread).start()

        self.active_dialog.dismiss()
        self.root.ids.bar_date_calendar.text = "No Date Selected"
        self.root.ids.date_tasks.clear_widgets()

    def save_checkbox_edits(self, card):
        current_page = self.active_page

        def update_thread(*l):
            thread_connection = sqlite3.connect('tasks.db')
            thread_cursor = thread_connection.cursor()

            # Execute the update query
            thread_cursor.execute("update tasks set completed=? where task_name=?", (card.ids.complete.active, card.ids.task.text))

            thread_connection.commit()
            thread_cursor.close()
            thread_connection.close()

            self.card_specified_update(active=current_page)
            
        Clock.schedule_once(update_thread, 1)

if __name__ == "__main__":
    MainApp().run()             # instance of MainApp and running it