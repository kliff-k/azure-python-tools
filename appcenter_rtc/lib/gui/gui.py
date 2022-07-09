import sys

from appcenter_rtc.lib.gui.main_window import MainWindow

from PySide6.QtGui import Qt
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication, QStyleFactory


def start_gui():
    """
    Executes the script in GUI mode
    :return: None
    """

    # Sets application DPI attributes
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # Instantiates application interface loop
    app = QApplication()
    app.setStyle(QStyleFactory.create('Fusion'))

    # Instantiates main window
    main_window = MainWindow()
    main_window.show()

    # Executes GUI application
    sys.exit(app.exec())
