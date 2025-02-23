import sys
import time
from datetime import date
from PyQt5 import QtGui, QtCore, QtWidgets

class Window(QtWidgets.QMainWindow):
    settings = QtCore.QSettings("PMSession.ini", QtCore.QSettings.IniFormat)
    def __init__(self, app):
        super(Window, self).__init__()
        self.setWindowTitle("Project Manager")
        #self.setWindowIcon(QtGui.QIcon('C:/Users/Antoine/Documents/ProjectManager/Icon.jpg'))
        self.setStyleSheet("QMainWindow {background: 'white';}")#White background


        #Variables
        self.current_task_id = -1
        self.current_task_object = None
        self.current_date = date(QtCore.QDate().currentDate().year(), QtCore.QDate().currentDate().month(), QtCore.QDate().currentDate().day()) #Format (yyyy mm dd)
        self.ScheduleContainerList = []

        #Save settings
        self.stored_task_bar_datas = []
        self.stored_pyramid_bar_datas = []
        self.stored_to_do_bar_datas = []
        self.stored_schedule_datas = []

        self.task_array = []
        self.pyramid_array = []
        self.to_do_task_array = []
        self.schedule_array = []

        #Layout declaration
        main_widget = QtWidgets.QWidget()
        self.main_h_box = QtWidgets.QHBoxLayout()
        self.left_v_box = QtWidgets.QVBoxLayout()
        self.left_splitted_v_box = QtWidgets.QSplitter()

        self.right_v_box = QtWidgets.QVBoxLayout()
        self.h_box_editor_schedule = QtWidgets.QHBoxLayout()
        self.h_box_pyramide_list = QtWidgets.QHBoxLayout()
        self.calendar_layout = QtWidgets.QHBoxLayout()

        #Custom class instances
        self.main_editor = Editor("Main Editor")
        self.main_editor.textEdit.setReadOnly(True)
        self.editor = Editor("Schedule Details")
        self.to_do_list_pannel = ToDoListPannel(self)
        self.task_creator = TaskCreator(self)
        self.task_list_pannel = TaskListPannel()
        self.pyramid_pannel = Pyramid()
        self.calendar = QtWidgets.QCalendarWidget(self)
        self.schedule = Schedule(self)

        #Load previous session
        Loader(self.settings, self.task_list_pannel, self.pyramid_pannel, self.to_do_list_pannel, self)

        #Scroll
        self.scroll_task = QtWidgets.QScrollArea()
        self.scroll_task.setWidget(self.task_list_pannel)
        self.scroll_task.setWidgetResizable(True)

        self.scroll_to_do_task = QtWidgets.QScrollArea()
        self.scroll_to_do_task.setWidget(self.to_do_list_pannel)
        self.scroll_to_do_task.setWidgetResizable(True)

        self.scroll_pyramid = QtWidgets.QScrollArea()
        self.scroll_pyramid.setWidget(self.pyramid_pannel)
        self.scroll_pyramid.setWidgetResizable(True)

        self.scroll_schedule = QtWidgets.QScrollArea()
        self.scroll_schedule.setWidget(self.schedule)
        self.scroll_schedule.setWidgetResizable(True)

        #Set layout
        self.right_widget = QtWidgets.QWidget()
        self.right_widget.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        main_widget.setLayout(self.main_h_box)
        self.setCentralWidget(main_widget)
        self.h_box_pyramide_list.addWidget(self.scroll_pyramid, 1)
        self.h_box_pyramide_list.addWidget(self.scroll_to_do_task, 1)
        self.left_v_box.addWidget(self.task_creator)
        #self.left_v_box.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed))
        self.left_v_box.addWidget(self.left_splitted_v_box, 1)
        #self.left_v_box.addLayout(self.h_box_pyramide_list, 2)
        self.left_splitted_v_box.setOrientation(QtCore.Qt.Vertical)
        self.left_splitted_v_box.addWidget(self.scroll_task)
        self.widget_for_splitter = QtWidgets.QWidget()
        self.widget_for_splitter.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred))
        self.widget_for_splitter.setLayout(self.h_box_pyramide_list)
        self.left_splitted_v_box.addWidget(self.widget_for_splitter)
        self.left_splitted_v_box.setStretchFactor(0, 5)
        self.left_splitted_v_box.setStretchFactor(1, 1)
        self.left_splitted_v_box.moveSplitter(50, 1)


        self.h_box_editor_schedule.addWidget(self.scroll_schedule, 1)
        self.h_box_editor_schedule.addWidget(self.editor, 1)
        self.calendar_layout.addWidget(self.calendar)
        self.right_v_box.addLayout(self.calendar_layout, 1)
        self.right_v_box.addLayout(self.h_box_editor_schedule, 1)
        self.right_widget.setLayout(self.right_v_box)
        self.main_tab = QtWidgets.QTabWidget()
        self.main_tab.addTab(self.main_editor, "Editor")
        self.main_tab.addTab(self.right_widget, "Schedule")

        self.main_tab.setCurrentIndex(1)
        self.main_h_box.addLayout(self.left_v_box, 1)
        self.main_h_box.addWidget(self.main_tab, 1)

        #Toolbar
        self.toolbar = self.addToolBar("Main Toolbar")
        action_save = QtWidgets.QAction(QtGui.QIcon('./imgs/save_icon.jpg'), 'Save', self)
        action_save.triggered.connect(self.Save)
        action_save.setShortcut(QtGui.QKeySequence("Ctrl+S"))
        action_help = QtWidgets.QAction(QtGui.QIcon('./imgs/help_icon.jpg'), 'Help', self)
        action_help.triggered.connect(self.Help)
        action_help.setShortcut(QtGui.QKeySequence("Ctrl+H"))
		#Adding tool to tool bar
        self.toolbar.addAction(action_save)
        self.toolbar.addAction(action_help)

        self.setWindowState(QtCore.Qt.WindowMaximized)

        #Style sheet
        self.setStyleSheet("QFrame{border: 1px solid rgb(0, 0, 0); background-color: rgb(255,255,255);}  QPushButton{background-color: rgb(0, 255, 0)} QCalendarWidget{ background-color: rgb(0,0,0);}")


        self.show()

        #Signal
        self.previous_date = self.current_date
        self.calendar.clicked.connect(self.CalendarLoad)

        self.current_calendar_date = self.calendar.selectedDate().toPyDate()

    def CalendarLoad(self, Date):
        self.current_calendar_date = Date.toPyDate()
        schedule_details_available = False



        for i in range(self.schedule.v_box.count() - 3):
            self.schedule.v_box.itemAt(3).widget().hide()
            self.schedule.v_box.removeWidget(self.schedule.v_box.itemAt(3).widget())

        for i in range(len(self.ScheduleContainerList)):
            if self.ScheduleContainerList[i].date == self.previous_date:
                self.ScheduleContainerList[i].schedule_details_text.setPlainText(self.editor.textEdit.toPlainText())
        for i in range(len(self.ScheduleContainerList)):
            if self.ScheduleContainerList[i].date == Date.toPyDate():
                schedule_details_available = True
                self.editor.textEdit.setReadOnly(False)
                self.editor.textEdit.setPlainText(self.ScheduleContainerList[i].schedule_details_text.toPlainText())
                for j in range(len(self.ScheduleContainerList[i].schedule_task_list)):
                    self.ScheduleContainerList[i].schedule_task_list[j].show()
                    self.schedule.v_box.addWidget(self.ScheduleContainerList[i].schedule_task_list[j])


        if schedule_details_available == False:
            self.editor.textEdit.setReadOnly(True)
            self.editor.textEdit.setPlainText("")

        self.previous_date = self.current_calendar_date

    def Save(self):
        #Reset arrays, otherwise datas would be copied each time we press SAVE
        self.stored_task_bar_datas = []
        self.stored_pyramid_bar_datas = []
        self.stored_to_do_bar_datas = []
        self.stored_schedule_datas = []

        if self.current_task_id != -1 and self.help_displayed == False:
            self.current_task_id = self.task_array.index(self.current_task_object)
            self.task_array[self.current_task_id].ProjectDevelopmentText.setPlainText(self.main_editor.textEdit.toPlainText())

        for i in range(len(self.task_array)):
            self.stored_task_bar_datas.append(self.task_array[i].task_name.text())
            self.stored_task_bar_datas.append(self.task_array[i].priority)
            self.stored_task_bar_datas.append(self.task_array[i].progress_bar.value())
            self.stored_task_bar_datas.append(i + 1)
            self.stored_task_bar_datas.append(self.task_array[i].dead_line_date)
            self.stored_task_bar_datas.append(self.task_array[i].initial_date)
            self.stored_task_bar_datas.append(self.task_array[i].ProjectDevelopmentText.toPlainText())
        for i in range(len(self.pyramid_array)):
            self.stored_pyramid_bar_datas.append(self.pyramid_array[i].task_name.text())
            self.stored_pyramid_bar_datas.append(self.pyramid_array[i].priority)
        for i in range(len(self.to_do_task_array)):
            self.stored_to_do_bar_datas.append(self.to_do_task_array[i].task_name.text())
        for i in range(len(self.ScheduleContainerList)):
            if self.ScheduleContainerList[i].date == self.current_calendar_date:
                self.ScheduleContainerList[i].schedule_details_text.setPlainText(self.editor.textEdit.toPlainText())
        for i in range(len(self.ScheduleContainerList)):
            if self.ScheduleContainerList[i].date >= self.current_date:
                self.stored_schedule_datas.append(QtCore.QDate(self.ScheduleContainerList[i].date).getDate())
                self.stored_schedule_datas.append(self.ScheduleContainerList[i].schedule_details_text.toPlainText())
                self.stored_schedule_datas.append(len(self.ScheduleContainerList[i].schedule_task_list))

                for j in range(len(self.ScheduleContainerList[i].schedule_task_list)):
                    self.stored_schedule_datas.append(self.ScheduleContainerList[i].schedule_task_list[j].hour.text())
                    self.stored_schedule_datas.append(self.ScheduleContainerList[i].schedule_task_list[j].task_name.text())
                    self.stored_schedule_datas.append(self.ScheduleContainerList[i].schedule_task_list[j].priority)
                    self.stored_schedule_datas.append(self.ScheduleContainerList[i].schedule_task_list[j].schedule_date)

        Saver(self.settings, self.stored_task_bar_datas, self.stored_pyramid_bar_datas, self.stored_to_do_bar_datas, self.stored_schedule_datas, self.editor.textEdit.toPlainText())

    def Help(self):
        if self.current_task_id != -1 and self.help_displayed == False:
            self.current_task_id = self.task_array.index(self.current_task_object)
            self.task_array[self.current_task_id].ProjectDevelopmentText.setPlainText(self.main_editor.textEdit.toPlainText())

        self.main_editor.textEdit.setPlainText("Help Doc")
        self.main_tab.setCurrentIndex(0)
        self.main_editor.textEdit.setReadOnly(True)
        self.help_displayed = True
        self.main_editor.title.setText("Help")

    def closeEvent(self, event):
        #Pop a Dialog box before leaving the app
        choice = QtWidgets.QMessageBox.question(self, "Extract", "Are you sure you want to leave?",
									QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if choice == QtWidgets.QMessageBox.Yes:
            sys.exit()
        else:
            event.ignore()


class TaskCreator(QtWidgets.QFrame):
    def __init__(self, main_win):
        super(TaskCreator, self).__init__()

        # Ref to the main window
        self.main_win = main_win

        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed))

        #QMessageBox
        self.dead_line_warning = QtWidgets.QMessageBox()
        self.dead_line_warning.setIcon(QtWidgets.QMessageBox.Critical)

        #Input text
        self.task_name = QtWidgets.QLineEdit(self)
        self.task_name.returnPressed.connect(self.AddTask)

        #Calendar
        self.calendar = QtWidgets.QCalendarWidget(self)
        self.calendar.hide()

        #Combo box
        self.priority = QtWidgets.QComboBox(self)
        self.start_progress = QtWidgets.QComboBox(self)

        #Buttons
        self.dead_line = QtWidgets.QPushButton("Dead-line", self)
        self.add_task = QtWidgets.QPushButton("add task", self)
        self.add_task.clicked.connect(self.AddTask)
        self.dead_line.clicked.connect(self.DeadLine)

        #Labels
        self.task_name_desc = QtWidgets.QLabel("Task name", self)
        self.priority_desc = QtWidgets.QLabel("Priority", self)
        self.dead_line_desc = QtWidgets.QLabel("Dead-line", self)
        self.start_progress_desc = QtWidgets.QLabel("Progress (%)", self)

		#Layout
        self.h_box_desc = QtWidgets.QHBoxLayout()
        self.h_box = QtWidgets.QHBoxLayout()
        self.v_box = QtWidgets.QVBoxLayout()

        self.h_box_desc.addWidget(self.task_name_desc, 5)
        self.h_box_desc.addWidget(self.priority_desc, 2)
        self.h_box_desc.addWidget(self.dead_line_desc, 3)
        self.h_box_desc.addWidget(self.start_progress_desc, 2)
        self.h_box_desc.addStretch(3)

        self.h_box.addWidget(self.task_name, 5)
        self.h_box.addWidget(self.priority, 2)
        self.h_box.addWidget(self.dead_line, 3)
        self.h_box.addWidget(self.start_progress, 2)
        self.h_box.addWidget(self.add_task, 3)

        self.v_box.addLayout(self.h_box_desc)
        self.v_box.addLayout(self.h_box)

        self.setLayout(self.v_box)

        #Set combo box
        for i in range(6):
            self.priority.addItem(str(i))

        for i in range(101):
            self.start_progress.addItem(str(i))


    def AddTask(self):

        self.chosen_date = date(self.calendar.selectedDate().year(), self.calendar.selectedDate().month(), self.calendar.selectedDate().day())

        if self.task_name.text() == "":
            self.dead_line_warning.setText("Please give your task a name")
            self.dead_line_warning.setWindowTitle("Warning no task name")
            self.dead_line_warning.setStandardButtons(QtWidgets.QMessageBox.Ok)
            self.dead_line_warning.exec_()

            self.h_box.removeWidget(self.calendar)
            self.calendar.hide()
            self.h_box.insertWidget(2, self.dead_line, 3)
            self.dead_line.show()

        if len(self.task_name.text()) > 20 :
            self.dead_line_warning.setText("Your task name must be under 20 caracters")
            self.dead_line_warning.setWindowTitle("Warning Task name too long!")
            self.dead_line_warning.setStandardButtons(QtWidgets.QMessageBox.Ok)
            self.dead_line_warning.exec_()

            self.h_box.removeWidget(self.calendar)
            self.calendar.hide()
            self.h_box.insertWidget(2, self.dead_line, 3)
            self.dead_line.show()

        if self.chosen_date == self.main_win.current_date:

            self.dead_line_warning.setText("The deadline is today, please choose a posterior date")
            self.dead_line_warning.setWindowTitle("Deadline Warning")
            self.dead_line_warning.setStandardButtons(QtWidgets.QMessageBox.Ok)
            self.dead_line_warning.exec_()

            self.h_box.removeWidget(self.calendar)
            self.calendar.hide()
            self.h_box.insertWidget(2, self.dead_line, 3)
            self.dead_line.show()

        if self.chosen_date < self.main_win.current_date:

            self.dead_line_warning.setText("Please, select an ulterior date")
            self.dead_line_warning.setWindowTitle("Dead-line error")
            self.dead_line_warning.setStandardButtons(QtWidgets.QMessageBox.Ok)
            self.dead_line_warning.exec_()

            self.h_box.removeWidget(self.calendar)
            self.calendar.hide()
            self.h_box.insertWidget(2, self.dead_line, 3)
            self.dead_line.show()

        elif (self.chosen_date > self.main_win.current_date) and self.task_name.text() != "" and len(self.task_name.text()) < 21:

            new_task = TaskBar(self.task_name.text(), int(str(self.priority.currentText())), int(str(self.start_progress.currentText())), len(self.main_win.task_array) + 1, self.main_win, self.chosen_date, self.main_win.current_date, "")
            new_pyramid_block = PyramidBlock(self.task_name.text(), int(str(self.priority.currentText())))

            item = QtGui.QStandardItem(new_task.task_name.text())

            if new_pyramid_block.priority == 0:
                item.setBackground(QtGui.QColor(255, 0, 0))
            if new_pyramid_block.priority == 1:
                item.setBackground(QtGui.QColor(206, 66, 244))
            if new_pyramid_block.priority == 2:
                item.setBackground(QtGui.QColor(66, 161, 244))
            if new_pyramid_block.priority == 3:
                item.setBackground(QtGui.QColor(244, 232, 66))
            if new_pyramid_block.priority == 4:
                item.setBackground(QtGui.QColor(244, 152, 66))
            if new_pyramid_block.priority == 5:
                item.setBackground(QtGui.QColor(0, 255, 0))

            self.inserted = False
            if not self.main_win.task_array:
                self.main_win.task_array.append(new_task)
                self.main_win.task_list_pannel.v_box.addWidget(new_task)
                self.main_win.pyramid_array.append(new_pyramid_block)
                self.main_win.pyramid_pannel.v_box.addWidget(new_pyramid_block)

                #ComboBox

                self.main_win.schedule.task_combo.model().insertRow(0, item)

            else:
                for i in range(len(self.main_win.task_array)):
                    if new_pyramid_block.priority < self.main_win.pyramid_array[i].priority:
                        self.main_win.task_array.insert(i, new_task)
                        self.main_win.task_array[i].id.setText(str(i + 1))
                        for j in range(i + 1, len(self.main_win.task_array)):
                            self.main_win.task_array[j].id.setText(str(int(self.main_win.task_array[j].id.text()) + 1))
                        self.main_win.pyramid_array.insert(i, new_pyramid_block)
                        self.main_win.schedule.task_combo.model().insertRow(i, item)
                        self.inserted = True
                        break
                if self.inserted == False:
                    self.main_win.task_array.append(new_task)
                    self.main_win.pyramid_array.append(new_pyramid_block)
                    self.main_win.schedule.task_combo.model().insertRow(len(self.main_win.task_array) - 1,item)


                self.main_win.task_list_pannel.v_box.insertWidget(self.main_win.task_array.index(new_task), new_task)
                self.main_win.pyramid_pannel.v_box.insertWidget(self.main_win.pyramid_array.index(new_pyramid_block)+2, new_pyramid_block)



            self.h_box.removeWidget(self.calendar)
            self.calendar.hide()
            self.h_box.insertWidget(2, self.dead_line, 3)
            self.dead_line.show()

            if self.main_win.current_task_id != -1:
                self.main_win.current_task_id = self.main_win.task_array.index(self.main_win.current_task_object)



    def DeadLine(self):

        self.h_box.removeWidget(self.dead_line)
        self.dead_line.hide()
        self.calendar.show()
        self.h_box.insertWidget(2, self.calendar, 3)



class TaskListPannel(QtWidgets.QFrame):
    def __init__(self):
        super(TaskListPannel, self).__init__()
        self.v_box = QtWidgets.QVBoxLayout()
        self.setLayout(self.v_box)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

class TaskBar(QtWidgets.QFrame):

    def __init__(self, name, priority, percentage, count, main_win, dead_line, initial_date, text_data):
        super(TaskBar, self).__init__()

        self.main_win = main_win

        self.priority = priority

        #PlainText
        self.ProjectDevelopmentText = QtWidgets.QPlainTextEdit()
        self.ProjectDevelopmentText.setPlainText(text_data)
        self.ProjectDevelopmentText.hide()

        #SizePolicy
        self.minimum_size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)

        #DeadLine
        self.dead_line_date = dead_line
        self.initial_date = initial_date

        #Variables
        self.days_count = (self.dead_line_date - self.main_win.current_date).days
        self.constant_day_interval = (self.dead_line_date - self.initial_date).days
        self.id_int = count - 1

        #Labels
        self.id = QtWidgets.QLabel(str(count), self)
        self.task_name = QtWidgets.QLabel(self)
        self.task_name.setText(name)

        self.task_name.setStyleSheet("QLabel {font-size: 15px;}")

        if self.priority == 0:
            self.id.setStyleSheet("QLabel {background-color : rgb(255, 0, 0); font-size: 15px;}")
        if self.priority == 1:
            self.id.setStyleSheet("QLabel {background-color : rgb(206, 66, 244); font-size: 15px;}")
        if self.priority == 2:
            self.id.setStyleSheet("QLabel {background-color : rgb(66, 161, 244); font-size: 15px;}")
        if self.priority == 3:
            self.id.setStyleSheet("QLabel {background-color : rgb(244, 232, 66); font-size: 15px;}")
        if self.priority == 4:
            self.id.setStyleSheet("QLabel {background-color : rgb(244, 152, 66); font-size: 15px;}")
        if self.priority == 5:
            self.id.setStyleSheet("QLabel {background-color : rgb(0, 255, 0); font-size: 15px;}")

        self.days_count_indicator = QtWidgets.QLabel("Days left: " + str(self.days_count))

        self.theoritical_percentage = ((self.constant_day_interval) - (self.days_count)) * (100) / self.constant_day_interval

        if self.theoritical_percentage >= 100:
            self.theoritical_percentage = 100

        self.task_name.setSizePolicy(self.minimum_size_policy)
        self.id.setSizePolicy(self.minimum_size_policy)
        self.days_count_indicator.setSizePolicy(self.minimum_size_policy)

        #Progress Bar
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setValue(percentage)
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: rgb(0, 255, 0);}")

        self.theoretical_progress_bar = QtWidgets.QProgressBar(self)
        self.theoretical_progress_bar.setValue(int(self.theoritical_percentage))
        self.theoretical_progress_bar.setStyleSheet("QProgressBar::chunk { background-color: blue;}")

        #Buttons
        self.remove_task = QtWidgets.QPushButton("Delete", self)
        self.remove_task.setStyleSheet("QPushButton{ background-color: rgb(255,0,0); }")
        self.plus_percentage = QtWidgets.QPushButton("+", self)
        self.minus_percentage = QtWidgets.QPushButton("-", self)
        self.add_sub_project = QtWidgets.QPushButton("Develop Project", self)
        self.add_sub_project.clicked.connect(self.DevelopProject)

		#Layout

        self.h_box = QtWidgets.QHBoxLayout()
        self.v_box_progress_bar = QtWidgets.QVBoxLayout()
        self.v_box = QtWidgets.QVBoxLayout()
        self.h_box.addWidget(self.id)
        self.h_box.addWidget(self.task_name, 1)
        self.v_box_progress_bar.addWidget(self.progress_bar, 1)
        self.v_box_progress_bar.addWidget(self.theoretical_progress_bar, 1)
        self.h_box.addLayout(self.v_box_progress_bar)
        self.h_box.addWidget(self.minus_percentage)
        self.h_box.addWidget(self.plus_percentage)
        self.h_box.addWidget(self.remove_task)
        self.h_box.addWidget(self.add_sub_project)
        self.h_box.addWidget(self.days_count_indicator)
        self.v_box.addLayout(self.h_box)
        self.setLayout(self.v_box)

		#Button connected
        self.plus_percentage.clicked.connect(self.PlusPercentage)
        self.minus_percentage.clicked.connect(self.MinusPercentage)
        self.remove_task.clicked.connect(self.remove_widget)

    def PlusPercentage(self):
        if self.progress_bar.value != 100:
            value = self.progress_bar.value() + 1
            self.progress_bar.setValue(value)
            #self.main_win.stored_task_bar_datas[self.main_win.stored_task_bar_datas.index(self.task_name.text()) + 1] = self.progress_bar.value()

    def MinusPercentage(self):
        if self.progress_bar.value != 0:
            value = self.progress_bar.value() - 1
            self.progress_bar.setValue(value)

    def remove_widget(self):
        clearLayout(self.main_win.task_list_pannel.v_box, self.main_win.task_array.index(self))
        clearLayout(self.main_win.pyramid_pannel.v_box, int(self.id.text()) + 1)


        for i in range(int(self.id.text()) - 1, len(self.main_win.task_array)):
            self.main_win.task_array[i].id.setText(str(int(self.main_win.task_array[i].id.text()) - 1))

        #Remove task from the schedule combobox
        self.main_win.schedule.task_combo.removeItem(self.main_win.task_array.index(self))

        del self.main_win.pyramid_array[self.main_win.task_array.index(self)]
        del self.main_win.task_array[self.main_win.task_array.index(self)]

        if self.main_win.current_task_object in self.main_win.task_array:
            self.main_win.current_task_id = self.main_win.task_array.index(self.main_win.current_task_object)
        else:
            self.main_win.current_task_id = - 1
            self.main_win.main_editor.textEdit.setPlainText("")
            self.main_win.main_editor.textEdit.setReadOnly(True)
            self.main_win.main_editor.title.setText("Main Editor")


    def DevelopProject(self):
        if self.main_win.current_task_id != -1 and self.main_win.help_displayed == False:
            self.main_win.current_task_id = self.main_win.task_array.index(self.main_win.current_task_object)
            self.main_win.task_array[self.main_win.current_task_id].ProjectDevelopmentText.setPlainText(self.main_win.main_editor.textEdit.toPlainText())

        self.main_win.main_tab.setCurrentIndex(0)
        self.main_win.main_editor.title.setText(self.task_name.text())
        self.main_win.current_task_id = self.main_win.task_array.index(self)
        self.main_win.current_task_object = self
        self.main_win.main_editor.textEdit.setPlainText(self.ProjectDevelopmentText.toPlainText())
        self.main_win.main_editor.textEdit.setReadOnly(False)
        self.main_win.help_displayed = False

class Pyramid(QtWidgets.QFrame):
    def __init__(self):
        super(Pyramid, self).__init__()

        #Label
        self.title = QtWidgets.QLabel("Priority", self)

        #Style sheet
        self.title.setStyleSheet("font : 20pt;")
        self.title.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum))
        self.title.setAlignment(QtCore.Qt.AlignHCenter)
        self.setStyleSheet("QLabel { font-size:20pt; }")

        #Layout
        self.v_box = QtWidgets.QVBoxLayout()
        self.v_box.addWidget(self.title)
        self.v_box.addStretch()
        self.setLayout(self.v_box)

class PyramidBlock(QtWidgets.QFrame):
    def __init__(self, name, priority):
        super(PyramidBlock, self).__init__()
        self.priority = priority

        #Layout
        self.h_box = QtWidgets.QHBoxLayout()
        self.v_box = QtWidgets.QVBoxLayout()
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        #Label
        self.task_name = QtWidgets.QLabel(name)
        self.task_name.setWordWrap(True)
        self.task_name.setAlignment(QtCore.Qt.AlignCenter)
        #self.task_name.setAlignment(QtCore.Qt.AlignVCenter)



        #Size Policy
        self.task_name.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.setStyleSheet("QWidget{border: none;}} ")

        if priority == 0:
            self.task_name.setStyleSheet("QLabel {background-color : rgb(255, 0, 0); border: 2px solid rgb(0, 0, 0); padding: 0 0 0 0; margin: 0 0 0 0;} QWidget{ margin: 0 0 0 0; padding: 0 0 0 0;}")
            self.task_name.setMargin(0)
            self.task_name.setIndent(0)
            self.h_box.addWidget(self.task_name)
        if priority == 1:
            self.task_name.setStyleSheet("QLabel {background-color : rgb(206, 66, 244); border: 2px solid rgb(0, 0, 0);}")
            self.h_box.addStretch(1)
            self.h_box.addWidget(self.task_name, 12)
            self.h_box.addStretch(1)
        if priority == 2:
            self.task_name.setStyleSheet("QLabel {background-color : rgb(66, 161, 244); border: 2px solid rgb(0, 0, 0);} ")
            self.h_box.addStretch(1.7)
            self.h_box.addWidget(self.task_name, 6.6)
            self.h_box.addStretch(1.7)
        if priority == 3:
            self.task_name.setStyleSheet("QLabel {background-color : rgb(244, 232, 66); border: 2px solid rgb(0, 0, 0);}")
            self.h_box.addStretch(2)
            self.h_box.addWidget(self.task_name, 6)
            self.h_box.addStretch(2)
        if priority == 4:
            self.task_name.setStyleSheet("QLabel {background-color : rgb(244, 152, 66); border: 2px solid rgb(0, 0, 0);}")
            self.h_box.addStretch(2.7)
            self.h_box.addWidget(self.task_name, 4.6)
            self.h_box.addStretch(2.7)
        if priority == 5:
            self.task_name.setStyleSheet("QLabel {background-color : rgb(0, 255, 0); border: 2px solid rgb(0, 0, 0);}")
            self.h_box.addStretch(3)
            self.h_box.addWidget(self.task_name, 4)
            self.h_box.addStretch(3)

        self.setContentsMargins(0, 0, 0, 0)
        self.h_box.setContentsMargins(0, 0, 0, 0)
        self.h_box.setSpacing(0)
        self.v_box.setContentsMargins(0, 0, 0, 0)
        self.v_box.setSpacing(0)
        self.v_box.addLayout(self.h_box)
        self.setLayout(self.v_box)

class ToDoListPannel(QtWidgets.QFrame):
    def __init__(self, main_win):
        super(ToDoListPannel, self).__init__()

        self.main_win = main_win

        #Warning
        self.warning_box = QtWidgets.QMessageBox()
        self.warning_box.setIcon(QtWidgets.QMessageBox.Critical)

        #Label
        self.title = QtWidgets.QLabel("To Do List", self)
        self.title.setStyleSheet("font : 20pt;")
        self.title.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum))
        self.title.setAlignment(QtCore.Qt.AlignHCenter)

        #Input
        self.task_name = QtWidgets.QLineEdit(self)
        self.task_name.returnPressed.connect(self.AddTask)

        #Buttons
        self.add_task = QtWidgets.QPushButton("Add task", self)

        #Connections
        self.add_task.clicked.connect(self.AddTask)

        self.v_box = QtWidgets.QVBoxLayout()
        self.h_box = QtWidgets.QHBoxLayout()
        self.h_box.addWidget(self.task_name)
        self.h_box.addWidget(self.add_task)

        self.v_box.addWidget(self.title)

        self.v_box.addLayout(self.h_box)
        self.v_box.addStretch()
        self.setLayout(self.v_box)

        self.setContentsMargins(0, 0, 0, 0)
        self.h_box.setContentsMargins(0, 0, 0, 0)
        self.h_box.setSpacing(0)
        self.v_box.setContentsMargins(0, 0, 0, 0)
        self.v_box.setSpacing(0)

    def AddTask(self):
        if len(self.task_name.text()) > 20 :
            self.warning_box.setText("Your task name must be under 20 caracters")
            self.warning_box.setWindowTitle("Warning Task name too long!")
            self.warning_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
            self.warning_box.exec_()

        elif len(self.task_name.text()) < 21:

            new_task_to_do = ToDoTask(self.task_name.text(), self.main_win)
            self.v_box.addWidget(new_task_to_do)
            self.main_win.to_do_task_array.append(new_task_to_do)

            #ComboBox
            item = QtGui.QStandardItem(self.task_name.text())
            item.setBackground(QtGui.QColor(128, 128, 128))
            self.main_win.schedule.task_combo.model().appendRow(item)

class ToDoTask(QtWidgets.QFrame):
    def __init__(self, name, main_win):
        super(ToDoTask, self).__init__()
        self.task_name = QtWidgets.QLabel(name, self)
        self.task_name.setAlignment(QtCore.Qt.AlignHCenter)
        self.task_name.setWordWrap(True)
        self.setStyleSheet("QLabel {background-color : rgb(128, 128, 128);} QWidget{border: none; font: 12pt;}")
        self.task_name.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum))
        self.main_win = main_win

        #Buttons
        self.remove_btn = QtWidgets.QPushButton("Remove", self)
        self.remove_btn.setStyleSheet("QPushButton{background-color: rgb(255, 0, 0);}")
        #Connections
        self.remove_btn.clicked.connect(self.remove_widget)

        #Layout
        self.h_box = QtWidgets.QHBoxLayout()
        self.h_box.addWidget(self.task_name, 1)
        self.h_box.addWidget(self.remove_btn, 1)
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.h_box)

    def remove_widget(self):
        clearLayout(self.main_win.to_do_list_pannel.v_box, self.main_win.to_do_task_array.index(self) + 3)
        self.main_win.schedule.task_combo.removeItem(len(self.main_win.task_array) + self.main_win.to_do_task_array.index(self))
        del self.main_win.to_do_task_array[self.main_win.to_do_task_array.index(self)]

class Schedule(QtWidgets.QFrame):
    def __init__(self, win):
        super(Schedule, self).__init__()

        self.main_win = win

        #Label
        self.title = QtWidgets.QLabel("Schedule")
        self.title.setAlignment(QtCore.Qt.AlignHCenter)
        self.title.setStyleSheet("QLabel {border: 2px solid rgb(0, 0, 0); font: 15pt;}")

        #C0mbobox
        self.hour = QtWidgets.QComboBox(self)
        self.hour.addItem("00h00")
        self.hour.addItem("00h30")
        self.hour.addItem("01h00")
        self.hour.addItem("01h30")
        self.hour.addItem("02h00")
        self.hour.addItem("02h30")
        self.hour.addItem("03h00")
        self.hour.addItem("03h30")
        self.hour.addItem("04h00")
        self.hour.addItem("04h30")
        self.hour.addItem("05h00")
        self.hour.addItem("05h30")
        self.hour.addItem("06h00")
        self.hour.addItem("06h30")
        self.hour.addItem("07h00")
        self.hour.addItem("07h30")
        self.hour.addItem("08h00")
        self.hour.addItem("08h30")
        self.hour.addItem("09h00")
        self.hour.addItem("09h30")
        self.hour.addItem("10h00")
        self.hour.addItem("10h30")
        self.hour.addItem("11h00")
        self.hour.addItem("11h30")
        self.hour.addItem("12h00")
        self.hour.addItem("12h30")
        self.hour.addItem("13h00")
        self.hour.addItem("13h30")
        self.hour.addItem("14h00")
        self.hour.addItem("14h30")
        self.hour.addItem("15h00")
        self.hour.addItem("15h30")
        self.hour.addItem("16h00")
        self.hour.addItem("16h30")
        self.hour.addItem("17h00")
        self.hour.addItem("17h30")
        self.hour.addItem("18h00")
        self.hour.addItem("18h30")
        self.hour.addItem("19h00")
        self.hour.addItem("19h30")
        self.hour.addItem("20h00")
        self.hour.addItem("20h30")
        self.hour.addItem("21h00")
        self.hour.addItem("21h30")
        self.hour.addItem("22h00")
        self.hour.addItem("22h30")
        self.hour.addItem("23h00")
        self.hour.addItem("23h30")

        self.task_combo = QtWidgets.QComboBox(self)
        self.task_combo.SelectionLength = 0

        #Button
        self.add_task_btn = QtWidgets.QPushButton("add task", self)
        self.add_task_btn.clicked.connect(self.AddTask)

       #Layout
        self.v_box = QtWidgets.QVBoxLayout()
        self.h_box = QtWidgets.QHBoxLayout()

        self.h_box.addWidget(self.hour, 1)
        self.h_box.addWidget(self.task_combo, 2)
        self.h_box.addWidget(self.add_task_btn, 1)

        self.v_box.addWidget(self.title)

        self.v_box.addLayout(self.h_box)
        self.v_box.addStretch()
        self.setLayout(self.v_box)

    def AddTask(self):
        self.main_win.editor.textEdit.setReadOnly(False)
        calendar_date = self.main_win.calendar.selectedDate()
        formated_date = date(calendar_date.year(), calendar_date.month(), calendar_date.day())

        if self.task_combo.count() != 0:
            inserted = False
            ScheduleContainedAlreadyExists = False
            schedule_container_id = 0

            if self.task_combo.currentIndex() >= len(self.main_win.pyramid_array):
                priority = -1
            else:
                priority = self.main_win.pyramid_array[self.task_combo.currentIndex()].priority

            new_task = ScheduleBar(self.hour.currentText(), self.task_combo.currentText(), priority,  self.main_win, self.main_win.calendar.selectedDate())

            for i in range(len(self.main_win.ScheduleContainerList)):
                if self.main_win.calendar.selectedDate().toPyDate() == self.main_win.ScheduleContainerList[i].date:
                    ScheduleContainedAlreadyExists = True
                    schedule_container_id = i

            if ScheduleContainedAlreadyExists == False:
                new_schedule_container = ScheduleContainer(formated_date, "")
                self.main_win.ScheduleContainerList.append(new_schedule_container)
                self.main_win.ScheduleContainerList[len(self.main_win.ScheduleContainerList) - 1].schedule_task_list.append(new_task)
                self.v_box.addWidget(new_task)

            else:
                for i in range(len(self.main_win.ScheduleContainerList[schedule_container_id].schedule_task_list)):
                    if int(str(new_task.hour.text()[:2]) + str(new_task.hour.text()[3:5])) < int(str(self.main_win.ScheduleContainerList[schedule_container_id].schedule_task_list[i].hour.text()[:2]) + str(self.main_win.ScheduleContainerList[schedule_container_id].schedule_task_list[i].hour.text()[3:5])):
                        self.v_box.insertWidget(i + 3, new_task)
                        self.main_win.ScheduleContainerList[schedule_container_id].schedule_task_list.insert(i, new_task)
                        inserted = True
                        break

                if inserted == False:
                    self.v_box.addWidget(new_task)
                    self.main_win.ScheduleContainerList[schedule_container_id].schedule_task_list.append(new_task)


        else:
            self.warning_message = QtWidgets.QMessageBox()
            self.warning_message.setText("No task to put in schedule")
            self.warning_message.setWindowTitle("No task")
            self.warning_message.setStandardButtons(QtWidgets.QMessageBox.Ok)
            self.warning_message.exec_()

class ScheduleContainer():
    def __init__(self, date, text):
        self.date = date
        self.schedule_task_list = []
        self.schedule_details_text = QtWidgets.QPlainTextEdit()
        self.schedule_details_text.setPlainText(text)
        self.schedule_details_text.hide()


class ScheduleBar(QtWidgets.QFrame):
    def __init__(self, hour, name, priority, win, date):
        super(ScheduleBar, self).__init__()

        self.schedule_date = date
        self.main_win = win
        self.priority = int(priority)

        #Label
        self.hour = QtWidgets.QLabel(hour)
        self.task_name = QtWidgets.QLabel(name)
        self.task_name.setAlignment(QtCore.Qt.AlignHCenter)

        #Buttons
        self.remove_task = QtWidgets.QPushButton("remove task", self)
        self.remove_task.clicked.connect(self.RemoveTask)

        #Layout
        self.h_box = QtWidgets.QHBoxLayout()
        self.h_box.addWidget(self.hour, 1)
        self.h_box.addWidget(self.task_name, 2)
        self.h_box.addWidget(self.remove_task, 1)
        self.setLayout(self.h_box)

        if self.priority == 0:
            self.task_name.setStyleSheet("QLabel {background-color : rgb(255, 0, 0); border: 2px solid rgb(0, 0, 0);} ")

        if self.priority == 1:
            self.task_name.setStyleSheet("QLabel {background-color : rgb(206, 66, 244); border: 2px solid rgb(0, 0, 0);} ")

        if self.priority == 2:
            self.task_name.setStyleSheet("QLabel {background-color : rgb(66, 161, 244); border: 2px solid rgb(0, 0, 0);} ")

        if self.priority == 3:
            self.task_name.setStyleSheet("QLabel {background-color : rgb(244, 232, 66); border: 2px solid rgb(0, 0, 0);} ")

        if self.priority == 4:
            self.task_name.setStyleSheet("QLabel {background-color : rgb(244, 152, 66); border: 2px solid rgb(0, 0, 0);} ")

        if self.priority == 5:
            self.task_name.setStyleSheet("QLabel {background-color : rgb(0, 255, 0); border: 2px solid rgb(0, 0, 0);} ")
        if self.priority == -1:
            self.task_name.setStyleSheet("QLabel {background-color : rgb(128, 128, 128); border: 2px solid rgb(0, 0, 0);} ")


    def RemoveTask(self):
        self.main_win.schedule.v_box.removeWidget(self)
        self.hide()
        for i in range(len(self.main_win.ScheduleContainerList)):
            if self.main_win.ScheduleContainerList[i].date == self.main_win.calendar.selectedDate().toPyDate():
                index = i

        del self.main_win.ScheduleContainerList[index].schedule_task_list[self.main_win.ScheduleContainerList[index].schedule_task_list.index(self)]

        if len(self.main_win.ScheduleContainerList[index].schedule_task_list) == 0:
            del self.main_win.ScheduleContainerList[index]


class Editor(QtWidgets.QFrame):
    def __init__(self, name):
        super(Editor, self).__init__()

        #Label
        self.title = QtWidgets.QLabel(name, self)
        self.title.setAlignment(QtCore.Qt.AlignHCenter)
        self.title.setStyleSheet("QLabel {border: 2px solid rgb(0, 0, 0); font: 15pt;}")
        self.title.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum))

        #Plain Text
        self.textEdit = QtWidgets.QPlainTextEdit(self)
        self.textEdit.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        #Layout
        self.v_box = QtWidgets.QVBoxLayout()
        self.v_box.addWidget(self.title)
        self.v_box.addWidget(self.textEdit)

        self.setLayout(self.v_box)


def Saver(settings, stored_task_bar_datas, stored_pyramid_bar_datas, stored_to_do_bar_datas, stored_schedule_datas, editor_datas):
    settings.setValue("stored_task_bar_datas", stored_task_bar_datas)
    settings.setValue("stored_pyramid_bar_datas", stored_pyramid_bar_datas)
    settings.setValue("stored_to_do_bar_datas", stored_to_do_bar_datas)
    settings.setValue("stored_schedule_datas", stored_schedule_datas)

def Loader(settings, task_board, pyramid_board, to_do_board, win):
    win.stored_task_bar_datas = settings.value("stored_task_bar_datas", [])
    win.stored_pyramid_bar_datas = settings.value("stored_pyramid_bar_datas", [])
    win.stored_to_do_bar_datas = settings.value("stored_to_do_bar_datas", [])
    win.stored_schedule_datas = settings.value("stored_schedule_datas", [])

    text_editor = settings.value("stored_editor_datas", "")
    main_editor = settings.value("stored_main_editor_datas", "")

    if win.stored_task_bar_datas is not None:
        for i in range(int(len(win.stored_task_bar_datas)/7)):
            new_task = TaskBar(win.stored_task_bar_datas[7 * i], int(win.stored_task_bar_datas[7 * i + 1]), int(win.stored_task_bar_datas[7 * i + 2]), int(win.stored_task_bar_datas[7 * i + 3]), win, win.stored_task_bar_datas[7 * i + 4], win.stored_task_bar_datas[7 * i + 5], win.stored_task_bar_datas[7 * i + 6])
            task_board.v_box.addWidget(new_task)
            win.task_array.append(new_task)


    if win.stored_task_bar_datas is not None:
        for i in range(int(len(win.stored_pyramid_bar_datas)/2)):
            pyramid = PyramidBlock(win.stored_pyramid_bar_datas[2 * i], int(win.stored_pyramid_bar_datas[2 * i + 1]))
            pyramid_board.v_box.addWidget(pyramid)
            win.pyramid_array.append(pyramid)

            #ComboBox
            item = QtGui.QStandardItem(win.task_array[i].task_name.text())

            if win.pyramid_array[i].priority == 0:
                item.setBackground(QtGui.QColor(255, 0, 0))
            if win.pyramid_array[i].priority == 1:
                item.setBackground(QtGui.QColor(206, 66, 244))
            if win.pyramid_array[i].priority == 2:
                item.setBackground(QtGui.QColor(66, 161, 244))
            if win.pyramid_array[i].priority == 3:
                item.setBackground(QtGui.QColor(244, 232, 66))
            if win.pyramid_array[i].priority == 4:
                item.setBackground(QtGui.QColor(244, 152, 66))
            if win.pyramid_array[i].priority == 5:
                item.setBackground(QtGui.QColor(0, 255, 0))

            win.schedule.task_combo.model().appendRow(item)

    #Insert separator in the Combobox
    #win.schedule.task_combo.insertSeparator(len(win.pyramid_array))
    if win.stored_to_do_bar_datas is not None:
        for i in range(int(len(win.stored_to_do_bar_datas))):
            to_do = ToDoTask(win.stored_to_do_bar_datas[i], win)
            to_do_board.v_box.addWidget(to_do)
            win.to_do_task_array.append(to_do)

            item = QtGui.QStandardItem(win.to_do_task_array[i].task_name.text())
            item.setBackground(QtGui.QColor(128, 128, 128))
            win.schedule.task_combo.model().appendRow(item)

    iterator = 0

    win.editor.textEdit.setReadOnly(True)
    if win.stored_schedule_datas is not None:
        while(iterator < int(len(win.stored_schedule_datas) - 1)):
            year, month, day = win.stored_schedule_datas[iterator]
            #print(year, month, day)
            formated_date = date(int(year), int(month), int(day))
            iterator = iterator + 1
            schedule_text = win.stored_schedule_datas[iterator]
            new_schedule_container = ScheduleContainer(formated_date, schedule_text)
            win.ScheduleContainerList.append(new_schedule_container)
            iterator = iterator + 1
            loop_sequence = int(win.stored_schedule_datas[iterator])

            if win.ScheduleContainerList[len(win.ScheduleContainerList) - 1].date == win.calendar.selectedDate().toPyDate():
                win.editor.textEdit.setPlainText(win.ScheduleContainerList[len(win.ScheduleContainerList) - 1].schedule_details_text.toPlainText())
                win.editor.textEdit.setReadOnly(False)
            for i in range(loop_sequence):
                new_schedule = ScheduleBar(win.stored_schedule_datas[iterator + 1], win.stored_schedule_datas[iterator + 2], win.stored_schedule_datas[iterator + 3], win, formated_date)
                win.ScheduleContainerList[len(win.ScheduleContainerList) - 1].schedule_task_list.append(new_schedule)
                if new_schedule.schedule_date == win.calendar.selectedDate().toPyDate():
                    win.schedule.v_box.addWidget(new_schedule)
                iterator = iterator + 4
                if i == loop_sequence - 1:
                    iterator = iterator + 1


    win.main_editor.textEdit.setPlainText(main_editor)

def clearLayout(layout, layout_index):
        #while layout.count():
        child = layout.takeAt(layout_index)
        if child.widget() is not None:
            child.widget().deleteLater()
        elif child.layout() is not None:
            clearLayout(child.layout())


def run():
    app = QtWidgets.QApplication(sys.argv)

    # Splash screen
    pixmap = QtGui.QPixmap("c:/Users/Antoine/Documents/ProjectManager/dixcipuli_icon_small.png")
    splash = QtWidgets.QSplashScreen(pixmap)
    splash.show()
    app.processEvents()

    GUI = Window(app)

    splash.finish(GUI)
    sys.exit(app.exec_())

run()