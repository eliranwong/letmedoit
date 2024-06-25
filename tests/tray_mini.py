import sys
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QAction, QGuiApplication

class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        super().__init__(icon, parent)

        self.menu = QMenu(parent)
        self.exitAction = QAction("Exit", self)
        self.exitAction.triggered.connect(self.exit)
        self.menu.addAction(self.exitAction)

        self.setContextMenu(self.menu)

    def exit(self):
        self.setVisible(False)
        QGuiApplication.instance().quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    icon = QIcon("/home/eliran/Desktop/image/image.jpg")
    trayIcon = SystemTrayIcon(icon)
    trayIcon.show()

    sys.exit(app.exec())
