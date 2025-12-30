from qgs.PyQt.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QProgressBar
import threading


class InstallDialog(QDialog):
    def __init__(self, packages):
        super().__init__()
        self.packages = packages
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.label = QLabel("Installing required packages...")
        layout.addWidget(self.label)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.setLayout(layout)

        self.setWindowTitle("Package Installer")
        self.setGeometry(300, 300, 300, 100)

        self.show()

        threading.Thread(target=self.install_packages).start()

    def install_packages(self):
        total = len(self.packages)
        for i, package in enumerate(self.packages):
            self.label.setText(f"Installing {package}...")
            self.progress.setValue((i + 1) / total * 100)
            install(package)
        self.label.setText("Installation complete")
        self.accept()


def show_install_dialog(packages):
    dialog = InstallDialog(packages)
    dialog.exec()
