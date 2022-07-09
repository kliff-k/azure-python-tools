import hashlib
import json

from appcenter_rtc.config import data_paths
from appcenter_rtc.lib.tool.aes import Cipher
from appcenter_rtc.lib.api.jazz_rtc import JazzRtc
from appcenter_rtc.lib.gui.worker import Worker
from appcenter_rtc.lib.api.app_center import AppCenter
from appcenter_rtc.lib.gui.utils import generate_encryption_key

from PySide6.QtGui import QIcon
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QDialog, QGridLayout, QLineEdit, QLabel, QPushButton, QHBoxLayout, QMessageBox


class LoginDialog(QDialog):
    """
    Login modal dialog window
    """
    def __init__(self):
        """
        Builds the dialog layout and widgets
        """
        super().__init__()

        # Sets up a thread pool for concurrent execution
        self.threadpool = QThreadPool()

        # Window information
        self.setWindowTitle("Login")
        self.setWindowIcon(QIcon(':/qt-project.org/logos/pysidelogo.png'))
        self.setFixedSize(200, 150)

        # Labels and text boxes are aligned with a Grid Layout
        layout = QGridLayout()

        # Text box widgets
        self.login_user = QLineEdit()
        self.login_pass = QLineEdit()
        self.login_api_token = QLineEdit()
        # Sets echo mode to "password" for user password input
        self.login_pass.setEchoMode(QLineEdit.Password)

        # Labels for the text box widgets
        login_user_label = QLabel("Usuário:")
        login_pass_label = QLabel("Senha:")
        login_token_label = QLabel("<a href='https://appcenter.ms/settings/apitokens'>API Token</a>:")
        # Enables external link functionality for AppCenter user token
        login_token_label.setOpenExternalLinks(True)

        # Creates a login button
        self.login_button = QPushButton("Login")

        # Creates a horizontal box layout to align the login button to the right of the window
        login_button_layout = QHBoxLayout()
        login_button_layout.addStretch()
        login_button_layout.addWidget(self.login_button)

        # Sets input widget signals to "save_user_info" slot
        self.login_button.clicked.connect(self.execute_user_input_process)
        self.login_user.returnPressed.connect(self.execute_user_input_process)
        self.login_pass.returnPressed.connect(self.execute_user_input_process)
        self.login_api_token.returnPressed.connect(self.execute_user_input_process)

        # Adds every widget to the grid layout
        layout.addWidget(login_user_label, 0, 0)
        layout.addWidget(self.login_user, 0, 1)
        layout.addWidget(login_pass_label, 1, 0)
        layout.addWidget(self.login_pass, 1, 1)
        layout.addWidget(login_token_label, 2, 0)
        layout.addWidget(self.login_api_token, 2, 1)
        layout.addLayout(login_button_layout, 3, 0, 1, 2)

        # Sets dialog layout
        self.setLayout(layout)

    def execute_user_input_process(self) -> None:
        """
        Parallel execution worker for the user login process
        """
        self.login_button.setText("Aguarde...")
        self.login_button.setDisabled(True)
        worker = Worker(self.save_user_info)
        worker.signals.result.connect(self.execute_login_result)

        self.threadpool.start(worker)

    def execute_login_result(self, result: str) -> None:
        """
        Login result response handler
        :param result: Worker return signal string
        """
        if result != 'success':
            QMessageBox.information(self, 'Erro', result)
            self.login_button.setText("Login")
            self.login_button.setDisabled(False)
        else:
            self.close()

    def save_user_info(self) -> str:
        """
        Saves user credential data to encrypted local storage
        :return local
        """

        # Validates user credentials before trying to save any data
        result = self.check_user_credentials()
        if result != 'success':
            return result

        # Fetches data from widgets
        user_data = {"username": self.login_user.text(),
                     "password": self.login_pass.text(),
                     "user_token": self.login_api_token.text()}

        # Saves the key hash
        encryption_key = generate_encryption_key()
        with open(data_paths.local_hash_file, 'w') as file:
            file.write(hashlib.sha3_512(encryption_key.encode()).hexdigest())

        # Save data
        aes = Cipher(encryption_key)
        with open(data_paths.local_data_file, 'wb') as file:
            file.write(aes.encrypt(json.dumps(user_data)))

        return 'success'

    def check_user_credentials(self) -> str:
        """
        Checks if provided credentials are valid
        :return bool
        """
        # Uses JazzRtc form login to validate credentials
        rtc = JazzRtc(self.login_user.text(), self.login_pass.text())
        if rtc.login_status == 200:
            return 'Login inválido.'

        # Tries to fetch an app list from AppCenter and check the result for key integrity / app read permissions
        ac = AppCenter(self.login_api_token.text())
        app_list = ac.get_app_list()
        if type(app_list) is dict and app_list['statusCode']:
            return 'Token inválido.'

        if not app_list:
            return 'Token não possui nenhum aplicativo vinculado.'

        return 'success'
