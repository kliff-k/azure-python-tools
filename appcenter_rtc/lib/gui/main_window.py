import sys
import natsort

from appcenter_rtc.lib.api.jazz_rtc import JazzRtc
from appcenter_rtc.lib.gui.worker import Worker
from appcenter_rtc.lib.api.app_center import AppCenter
from appcenter_rtc.lib.gui.login_dialog import LoginDialog
from appcenter_rtc.lib.gui.utils import check_user_data, get_user_data

from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QTimer, QThreadPool
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QComboBox, QGridLayout, QGroupBox, QPushButton, QTextBrowser,
                               QTabWidget, QProgressBar, QSpinBox, QMainWindow, QLabel)


class MainWindow(QMainWindow):
    """
    Gui operation mode class
    """

    def __init__(self):
        super().__init__()

        # Sets window app title and icon
        self.setWindowTitle("AppCenter -> RTC")
        self.setWindowIcon(QIcon(':/qt-project.org/logos/pysidelogo.png'))

        # Displays login dialog if no (valid) local user data is found
        if not check_user_data():
            login_dialog = LoginDialog()
            login_dialog.exec()

        # If login dialog is closed without creating valid user data, close the program
        if not check_user_data():
            sys.exit()

        # Sets up a thread pool for concurrent execution
        self.threadpool = QThreadPool()

        # Runtime data
        user_data = get_user_data()
        self.ac_data = {}
        self.rtc_data = {}

        # Service instances
        self.__ac = AppCenter(user_data['user_token'])
        self.__rtc = JazzRtc(user_data['username'], user_data['password'])

        # Global elements
        self.app_combobox = None
        self.version_combobox = None
        self.app_info_text = None
        self.community_combobox = None
        self.po_combobox = None
        self.team_combobox = None
        self.iteration_combobox = None
        self.error_groups = None
        self.result_logs = None
        self.query_button = None
        self.register_button = None
        self.query_register_button = None

        # Creates main window menu bar
        self.create_menu_bar()

        # Creates each element group layout
        appcenter_groupbox = self.create_appcenter_groupbox()
        jazz_rtc_groupbox = self.create_jazz_rtc_groupbox()
        button_groupbox = self.create_button_groupbox()
        tabs_box = self.create_tabs_box()
        self.progress_bar = self.create_progress_bar()

        # Creates a grid layout and places each element group in a symmetric box configuration
        layout = QGridLayout()
        layout.addWidget(appcenter_groupbox, 0, 0)
        layout.addWidget(jazz_rtc_groupbox, 0, 1)
        layout.addLayout(button_groupbox, 1, 0, 1, 2)
        layout.addWidget(tabs_box, 2, 0, 1, 2)
        layout.addWidget(self.progress_bar, 3, 0, 1, 2)

        # Sets the created grid layout and it's widgets as the main window central widget
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Populates the starting combo boxes with AppCenter and Jazz RTC data
        self.populate_app_combo()
        self.populate_community_combo()

    def create_menu_bar(self) -> None:
        """
        Creates the main window menu bar and define its actions
        """
        menu_bar = self.menuBar()
        menu_bar.addMenu("&Arquivo")
        options_menu = menu_bar.addMenu("&Opções")
        options_menu.addAction(QAction("&Login"))
        menu_bar.addMenu("&Ajuda")

    def create_appcenter_groupbox(self) -> QGroupBox:
        """
        Creates the AppCenter input group box layout, widgets and its actions
        """
        result = QGroupBox("AppCenter")

        # App selection combobox
        label_app_combobox = QLabel("App:")
        self.app_combobox = QComboBox()
        self.app_combobox.setPlaceholderText("Selecione o app")
        self.app_combobox.addItems([])
        self.app_combobox.activated.connect(self.execute_populate_versions_combo)
        self.app_combobox.activated.connect(self.populate_app_info)

        # Version selection combobox
        label_version_combobox = QLabel("Versão:")
        self.version_combobox = QComboBox()
        self.version_combobox.setPlaceholderText("Selecione a versão")
        self.version_combobox.addItems([])

        # Top integer spinner selector for total rows returned
        label_rows_spinbox = QLabel("Registros:")
        rows_spinbox = QSpinBox()
        rows_spinbox.setValue(10)

        # Information box for the selected app
        app_info_box = QGroupBox()
        app_info_box_layout = QHBoxLayout(app_info_box)
        self.app_info_text = QLabel("--")
        app_info_box_layout.addWidget(self.app_info_text)
        app_info_box_layout.setContentsMargins(5, 5, 5, 5)

        # Grid layout disposition
        ac_groupbox_layout = QGridLayout(result)
        ac_groupbox_layout.addWidget(label_app_combobox, 0, 0)
        ac_groupbox_layout.addWidget(self.app_combobox, 0, 1)
        ac_groupbox_layout.addWidget(label_version_combobox, 1, 0)
        ac_groupbox_layout.addWidget(self.version_combobox, 1, 1)
        ac_groupbox_layout.addWidget(label_rows_spinbox, 2, 0)
        ac_groupbox_layout.addWidget(rows_spinbox, 2, 1)
        ac_groupbox_layout.addWidget(app_info_box, 3, 0, 1, 2)

        return result

    def create_jazz_rtc_groupbox(self) -> QGroupBox:
        """
        Creates the Jazz RTC input group box layout, widgets and its actions
        """
        result = QGroupBox("Jazz RTC")

        # Community/project area selection combobox
        label_community_combobox = QLabel("Comunidade:")
        self.community_combobox = QComboBox()
        self.community_combobox.setPlaceholderText("Selecione a comunidade")
        self.community_combobox.addItems([])
        self.community_combobox.setEditable(True)
        self.community_combobox.activated.connect(self.execute_populate_rtc_combos)

        # Product Owner selection combobox
        label_po_combobox = QLabel("Dono do produto:")
        self.po_combobox = QComboBox()
        self.po_combobox.setPlaceholderText("Selecione o PO")
        self.po_combobox.addItems([])

        # Team selection combobox
        label_team_combobox = QLabel("Time:")
        self.team_combobox = QComboBox()
        self.team_combobox.setPlaceholderText("Selecione o time")
        self.team_combobox.addItems([])

        # Timeline/iteration selection combobox
        label_iteration_combobox = QLabel("Iteração:")
        self.iteration_combobox = QComboBox()
        self.iteration_combobox.setPlaceholderText("Selecione a iteração")
        self.iteration_combobox.addItems([])

        # Grid layout disposition
        rtc_groubbox_layout = QGridLayout(result)
        rtc_groubbox_layout.addWidget(label_community_combobox, 0, 0)
        rtc_groubbox_layout.addWidget(self.community_combobox, 0, 1)
        rtc_groubbox_layout.addWidget(label_po_combobox, 1, 0)
        rtc_groubbox_layout.addWidget(self.po_combobox, 1, 1)
        rtc_groubbox_layout.addWidget(label_team_combobox, 2, 0)
        rtc_groubbox_layout.addWidget(self.team_combobox, 2, 1)
        rtc_groubbox_layout.addWidget(label_iteration_combobox, 3, 0)
        rtc_groubbox_layout.addWidget(self.iteration_combobox, 3, 1)

        return result

    def create_button_groupbox(self) -> QHBoxLayout:
        """
        Creates the execution buttons layout and actions
        """
        button_layout = QHBoxLayout()

        # Action buttons
        self.query_button = QPushButton("Consultar")
        self.register_button = QPushButton("Registrar")
        self.query_register_button = QPushButton("Consultar e Registrar")

        # Horizontal placement
        button_layout.addWidget(self.query_button)
        button_layout.addWidget(self.register_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self.query_register_button)

        return button_layout

    def create_tabs_box(self) -> QTabWidget:
        """
        Creates the runtime information text browser tabs
        """
        result = QTabWidget()

        # Simple text browsers for information display
        self.error_groups = QTextBrowser()
        self.result_logs = QTextBrowser()

        # Browser position layout configuration
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.error_groups)
        result.addTab(widget, "Grupos de Erros")

        # Browser position layout configuration
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.result_logs)
        result.addTab(widget, "Resultado")

        return result

    def create_progress_bar(self) -> QProgressBar:
        """
        Creates the runtime progress bar
        """
        result = QProgressBar()
        result.setObjectName("progressBar")
        result.setRange(0, 10000)
        result.setValue(0)

        # Connects to execution slot
        timer = QTimer(self)
        timer.timeout.connect(self.advance_progressbar)
        timer.start(1000)
        return result

    def advance_progressbar(self) -> None:
        """
        Progress bar execution slot (temp)
        """
        cur_val = self.progress_bar.value()
        max_val = self.progress_bar.maximum()
        self.progress_bar.setValue(cur_val + (max_val - cur_val) / 100)

    def execute_populate_versions_combo(self) -> None:
        """
        Parallel execution worker for the app version combo box content loading
        """
        self.version_combobox.clear()
        self.version_combobox.setPlaceholderText('Carregando...')
        worker = Worker(self.populate_versions_combo)

        self.threadpool.start(worker)

    def execute_populate_rtc_combos(self) -> None:
        """
        Parallel execution worker for the Jazz RTC combo boxes content loading
        """
        self.po_combobox.clear()
        self.po_combobox.setPlaceholderText('Carregando...')
        self.team_combobox.clear()
        self.team_combobox.setPlaceholderText('Carregando...')
        self.iteration_combobox.clear()
        self.iteration_combobox.setPlaceholderText('Carregando...')

        worker1 = Worker(self.populate_po_combo)
        worker2 = Worker(self.populate_team_combo)
        worker3 = Worker(self.populate_iteration_combo)

        self.threadpool.start(worker1)
        self.threadpool.start(worker2)
        self.threadpool.start(worker3)

    def populate_app_combo(self) -> None:
        """
        Populates the app list combo box with the endpoint query result
        """
        app_list = self.__ac.get_app_list()

        # Organizes the api response into a dictionary
        new_dict = {}
        for app in app_list:
            new_dict[app['name']] = {'os': app['os'], 'env': app['release_type']}

        # Saves the sorted list for subsequent uses
        self.ac_data['app_list'] = dict(sorted(new_dict.items()))

        # Returns the keys (app names)
        self.app_combobox.addItems(self.ac_data['app_list'].keys())

    def populate_app_info(self) -> None:
        """
        Populates the app info text box with the selected app os and env information
        """
        index = self.app_combobox.currentText()
        info = f"OS: {self.ac_data['app_list'][index]['os']} - Env: {self.ac_data['app_list'][index]['env']}"

        self.app_info_text.setText(info)

    def populate_versions_combo(self) -> None:
        """
        Populates the app version combo box with the endpoint query result
        """
        index = self.app_combobox.currentText()
        version_list = self.__ac.get_app_versions(index, "500")['versions']

        # Fetches only the last 5 versions
        self.ac_data['version_list'] = natsort.natsorted(version_list, reverse=True)[:5]

        self.version_combobox.clear()
        self.version_combobox.setPlaceholderText('Selecione a versão')
        self.version_combobox.addItems(self.ac_data['version_list'])

    def populate_community_combo(self):
        """
        Populates the community/project list combo box with the endpoint query result
        """
        project_list = self.__rtc.project_areas()

        # Saves the sorted list for subsequent uses
        self.rtc_data['project_list'] = dict(sorted(project_list.items()))

        # Returns the keys (project names)
        self.community_combobox.addItems(project_list.keys())

    def populate_po_combo(self) -> None:
        """
        Populates the member list combo box with the endpoint query result
        """
        # TODO: REMOVE HARDCODED CREDENTIALS
        member_list = self.__rtc.members('', 'silva')

        # Saves the sorted list for subsequent uses
        self.rtc_data['member_list'] = dict(sorted(member_list.items()))

        self.po_combobox.clear()
        self.po_combobox.setPlaceholderText('Selecione o dono')
        self.po_combobox.addItems(member_list.keys())

    def populate_team_combo(self) -> None:
        """
        Populates the team combo box with the endpoint query result
        """
        # TODO: REMOVE HARDCODED CREDENTIALS
        team_list = self.__rtc.teams('')

        # Organizes the api response into a list
        new_list = []
        for team in team_list:
            new_list.append(team['name'])

        new_list.sort()

        # Saves the sorted list for subsequent uses
        self.rtc_data['team_list'] = new_list

        self.team_combobox.clear()
        self.team_combobox.setPlaceholderText('Selecione o time')
        self.team_combobox.addItems(self.rtc_data['team_list'])

    def populate_iteration_combo(self) -> None:
        """
        Populates the timeline/iteration combo box with the endpoint query result
        """
        # TODO: REMOVE HARDCODED CREDENTIALS
        iteration_list = self.__rtc.timeline_iterations('')

        # Organizes the api response into a dictionary
        new_dict = {}
        for iteration in iteration_list:
            if 'iterations' in iteration:
                iter_list = iteration['iterations']
            else:
                iter_list = []

            new_dict[iteration['name']] = {'iterations': iter_list}

        self.rtc_data['iteration_list'] = dict(sorted(new_dict.items()))

        self.iteration_combobox.clear()
        self.iteration_combobox.setPlaceholderText('Selecione a iteração')
        self.iteration_combobox.addItems(new_dict.keys())
