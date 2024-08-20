import sys
import webbrowser
import os
import io
import logging
import subprocess
import zipfile
from functools import partial

import py7zr
import shutil
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar, QHBoxLayout, \
    QToolButton
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer, QSize

# Встроенное содержимое style.qss
style_qss = """
QLabel#title {
    color: white;
    font-size: 24px;
    font-weight: bold;
    text-align: center;
}

QPushButton {
    background-color: #444;
    color: white;
    border-radius: 5px;
    padding: 10px;
}

QLabel {
    color: white;
}

QPushButton:hover {
    background-color: #666;
}

QProgressBar {
    background-color: #ccc;
    border-radius: 5px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #0057e7;
    width: 20px;
}
QToolButton {
    background-color: black;
    border: none;
    background: transparent;
    padding: 0px;
}
"""

# Инициализация API Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']
credentials_info = {
    "type": "service_account",
    "project_id": "kiberone-422110",
    "private_key_id": "1fde9ff94ad4ebe5b911559ca3ffaa337ef95141",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC5L1L8uTKSoXtr\n2SiF/ICNc2vaWm7JwSXKpto1TF7pBJlPxGGZ6BHynHY3R9sBo9WpCzu70r7M/Bvw\noPbOw4+XwHDmNYCXiRNLg66bkp+ziJKcdK0Z1HPPDhb1zL1yrzQIE7MzxChgba/m\n8ZX4mPBUBwpkE2fEdRk0ZhF148NSglwikiqQljG8HtwaOTFFIRSAkFNQUIbv4CdD\n6iaiY8qtD2vxs2w8O999eZM4661iF12JKis94Q88rI8QiYtRBNKf5WDOa/JbiCEU\nz6BZaNwostWqkeXgXT3MFqqSF2rACHFsvgNSi1hNlqN0mbq6vZyzSyarfABz3A3W\nr+5ItihdAgMBAAECggEAKeJ5S637sUyS5M7GKp/014l+oHGJ01o7WP2qJxnx8ZRX\ntMH/LVdfD9exqUk4UMOkpMpkpVPCUgzHqQJPMG7tAG7HWlpJjnyzf4X2LTvZoTrH\nplmBeXEjDHbsXIYFZ3YXN6h1BMVeOIk2mu6TdBnraaX6BK6a7sVpgP+A/YAZgoST\n63N8K48yV8NxsEIgE73yKDNuVVWI7FJPvtAux0f5uVlDyXiwWqTalK50MNicSBDC\nr9RpRQNrABTghxNtnI94D8GFWQfYGrgDfD4hn5F/OSGjfOqsGITYsAE+jrbxDu59\nB8iWuIpxWxHxgks4ApOea6zA4PUD43dQKq/vQu43hQKBgQD+rnuO0ZF0mVesXIz6\nE1FPNBsolnQUeYXWUqjhZ0mQaEg3XU7rNsffJqHitpt6cfkx3UVfqSJ9fPQ8JIJ3\nxilczz0dvy5+fuQPMskvTyzbC5KahIw8uMWaFPtMEmwaVXmvXuRnwN+kh6rfyhdn\njp4WUEpVBcGX+oGX81O1yqohOwKBgQC6JL2noKIpJV9Qa/gqUCfIXsnry+k5Cl+0\nEpr/XSWS/6l2m/Lm5Nw1F1sRbPhtpVYHDELdnw9t692MaojVrgkqFImSD/ZLxHXQ\n6DKEoT7FbvkV4vVJxEDwMQDDTpzLKNn0Sgbh0rDv3Y8dlte9RLAqQtNI0YuOVv+6\nVLjGITXDRwKBgBS8cCL4vTcZJSJLhs71s7EXNP7hASKJonQI1udDWaIAW6DmX/6W\nvz9UDeo/o/kcPoXo1jUruDsvaVNcRaMq50M/PGKnpkl2W2tBX1ASyjwrfQxHroNj\nJ/ObsbpH5bVfMEEvILmx4oOq6CbAdZdg7U4zy1mQ1mphYxvUHAS5M5DxAoGAeweV\nopl1FKTy3oC+QZlA8hpUc1kPCPhmUOqLL4UtNH9uTkq8vQc+1IhfVKElgbLprTbZ\nawmadRiUEh7H2hNxUzLHypZqP6HWDQGrgiXhCzVRxLmBTgQ8t4Rr8Kqgz1Zs2B2l\ndtR+xcs2sGPmq94eYZBRfauiBa5Sz6D3j1yb4DkCgYBUB+RjFPSqNQ1JQQAsxT5p\nKr7QLa8idKCJVUJfR0LCdtT2YNPcNFiGNtbFXflKuVZB9hciuSjxySt/yM++8XJQ\nxzeRSabfaeySCbTrHEpJeEegnAZ9OJhHadsm/HgRmHODqxCVokhoSYn+OxjzXeun\nm8e3JMCsdL6AX+oRz/vRyA==\n-----END PRIVATE KEY-----\n",
    "client_email": "bookingtest@kiberone-422110.iam.gserviceaccount.com",
    "client_id": "111582459063203248377",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/bookingtest%40kiberone-422110.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}
credentials = service_account.Credentials.from_service_account_info(
    credentials_info)
service = build('drive', 'v3', credentials=credentials)

FOLDER_ID = '1-ZJfs05U-aTmu2saVtdJQn3GibxzXQbo'
LOCAL_VERSION_FILE = 'version.txt'
REMOTE_VERSION_FILE = 'remote_version.txt'
LOCAL_UPDATE_FILE = 'update.7z'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
                        logging.FileHandler("launcher.log"),  # Логирование в файл
                        logging.StreamHandler(sys.stdout)           # Логирование в консоль
                    ])

logger = logging.getLogger(__name__)


def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)

    return os.path.join(base_path, relative_path)


FOOTER_BUTTONS_ICONS = (
    (resource_path("assets/Patron.png"),
     "https://www.patreon.com/RFaD_ChickenEdition/membership"),
    (resource_path("assets/Discord.png"),
     "https://discord.gg/q2ygjdk8Gv"),
    (resource_path("assets/mo2.png"),
     "https://boosty.to/skyrim_rfad_chicken"),
    (resource_path("assets/book.png"),
     "https://docs.google.com/spreadsheets/d/1XsKJBINxQxzXa2TtUoSLqt1Kp0-03Sz2tZ65PlJY94M/edit?gid=1184182319#gid=1184182319&range=A1"),
    (resource_path("assets/boosty.png"),
     "https://boosty.to/skyrim_rfad_chicken")
)


def open_link(link: str) -> None:
    browser = webbrowser.get()
    browser.open_new_tab(link)


class VersionCheckThread(QThread):
    versionCheckCompleted = pyqtSignal(str, str)

    def __init__(self, service, game_path):
        super().__init__()
        self.service = service
        self.game_path = game_path

    def run(self):
        files = self.get_drive_files()
        version_file = next(
            (f for f in files if f['mimeType'] == 'application/vnd.google-apps.document'),
            None)

        if not version_file:
            self.versionCheckCompleted.emit(None, None)
            return

        local_version_path = os.path.join(
            self.game_path,
            'MO2/mods/RFAD_PATCH',
            LOCAL_VERSION_FILE)
        self.download_file(
            service,
            version_file['id'],
            'remote_version.txt',
            version_file['mimeType'])

        with open(local_version_path, 'r') as file:
            local_version = file.read().strip()
        try:
            with open('remote_version.txt', 'r', encoding='utf-8-sig') as file:
                remote_version = file.read().strip()
                self.versionCheckCompleted.emit(local_version, remote_version)
        except FileNotFoundError:
            logger.error("Файл версии игры не найден")



    def download_file(self, service, file_id, destination, mime_type=None):
        if mime_type == 'application/vnd.google-apps.document':
            request = service.files().export_media(fileId=file_id, mimeType='text/plain')
        else:
            request = service.files().get_media(fileId=file_id)

        fh = io.FileIO(destination, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False

        while not done:
            status, done = downloader.next_chunk()
            if status:
                logger.info(f"Загрузка {int(status.progress() * 100)}%.")
        fh.close()

        logger .info(f"Файл {destination} успешно загружен.")

    def get_drive_files(self):
        results = self.service.files().list(
            q=f"'{FOLDER_ID}' in parents",
            pageSize=10,
            fields="files(id, name, mimeType)").execute()
        return results.get('files', [])


class DownloadThread(QThread):
    progressChanged = pyqtSignal(int)
    downloadFinished = pyqtSignal()

    def __init__(self, service, file_id, file_name):
        super().__init__()
        self.service = service
        self.file_id = file_id
        self.file_name = file_name

    def run(self):
        request = self.service.files().get_media(fileId=self.file_id)
        with io.FileIO(self.file_name, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            last_progress = 0
            while not done:
                status, done = downloader.next_chunk()
                progress = int(status.progress() * 100)
                if progress != last_progress:
                    self.progressChanged.emit(progress)
                    last_progress = progress
        self.downloadFinished.emit()


class SkyrimLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        # Определение пути к папке с игрой (текущая директория)
        self.game_path = os.path.abspath(os.getcwd())
        #self.selected_game_folder.setText(f'Game folder: {self.game_path}')

        # Асинхронная проверка обновлений после отображения окна
        self.check_updates_async()

        # Таймер для обновления интерфейса
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(100)  # Обновление каждые 100 мс

    def update_background(self):
        pixmap = QPixmap('assets/background2.png')
        palette = self.palette()
        scaled_pixmap = pixmap.scaled(
            self.size(),
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation)
        palette.setBrush(QPalette.Background, QBrush(scaled_pixmap))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.update_background()
        super().resizeEvent(event)

    def initUI(self):
        #self.setWindowTitle('RFAD Game Launcher')
        self.setGeometry(200, 200, 800, 480)

        # Установка фонового изображения
        self.update_background()

        layout = QVBoxLayout()

        #self.title = QLabel('RFAD Game Launcher', self)
        #self.title.setObjectName('title')
        #layout.addWidget(self.title)

        # self.selected_game_folder = QLabel('Game folder: None', self)
        # layout.addWidget(self.selected_game_folder)

        # self.update_status = QLabel('Status: Initializing...', self)
        # layout.addWidget(self.update_status)
        #
        # self.local_version = QLabel('Local Version: N/A', self)
        # layout.addWidget(self.local_version)
        #
        # self.online_version = QLabel('Online Version: N/A', self)
        # layout.addWidget(self.online_version)

        # self.update_button = QPushButton('Update', self)
        # self.update_button.setVisible(False)
        # self.update_button.clicked.connect(self.start_update)
        # layout.addWidget(self.update_button)
        # hbox = QHBoxLayout()
        # hbox.
        # layout.addLayout(hbox)
        layout.addStretch(1)
        for _ in range(4):
            button = QToolButton(self)
            button.setIcon(QIcon(resource_path("assets/middle-button.png")))
            button.setIconSize(QSize(400, 50))
            button.setToolButtonStyle(Qt.ToolButtonIconOnly)

            hbox = QHBoxLayout()
            hbox.addStretch(1)
            hbox.addWidget(button)
            hbox.addStretch(1)
            layout.addLayout(hbox)


        # self.button2 = QToolButton(self)
        # self.button2.setIcon(QIcon(resource_path("assets/middle-button.png")))
        # self.button2.setIconSize(QSize(500, 50))
        # self.button2.setToolButtonStyle(Qt.ToolButtonIconOnly)
        # self.play_button.clicked.connect(self.play_game)
        #
        # layout.addStretch(1)
        #
        # # Создаем горизонтальный layout для центрирования кнопки по горизонтали
        # hbox = QHBoxLayout()
        # hbox.addStretch(1)  # Растяжение слева
        # hbox.addWidget(self.button1) # Добавляем кнопку
        # hbox.addStretch(1)  # Растяжение справа
        #
        # # Добавляем горизонтальный layout в вертикальный
        # layout.addLayout(hbox)
        #
        # # Добавляем растяжение снизу
        # layout.addStretch(1)

        # Устанавливаем основной layout для виджета
        layout.addStretch(1)
        self.setLayout(layout)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        for url_icon, link in FOOTER_BUTTONS_ICONS:
            button = QToolButton(self)
            button.setIcon(QIcon(url_icon))
            button.setIconSize(QSize(75, 75))
            button.setToolButtonStyle(Qt.ToolButtonIconOnly)
            button.clicked.connect(partial(open_link, link=link))
            button_layout.addWidget(button)
        button_layout.addStretch(1)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def check_updates_async(self):
        self.version_thread = VersionCheckThread(service, self.game_path)
        self.version_thread.versionCheckCompleted.connect(
            self.on_version_check_completed)
        self.version_thread.start()

    def on_version_check_completed(self, local_version, remote_version):
        if local_version is None or remote_version is None:
            self.update_status.setText(
                'Status: Required files not found on Google Drive')
            return

        # self.local_version.setText(f'Local Version: {local_version}')
        # self.online_version.setText(f'Online Version: {remote_version}')
        #
        # if local_version != remote_version:
        #     self.update_status.setText('Status: Update available')
        #     self.update_button.setVisible(True)
        # else:
        #     self.update_status.setText('Status: Up to date')
        #     self.update_button.setVisible(False)

    def start_update(self):
        if not self.game_path:
            self.update_status.setText('Status: No game path set')
            return

        files = self.get_drive_files()
        update_file = next(
            (f for f in files if f['mimeType'] in [
                'application/x-7z-compressed',
                'application/x-zip-compressed']),
            None)
        if not update_file:
            self.update_status.setText('Status: Update file not found')
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.download_thread = DownloadThread(
            service, update_file['id'], LOCAL_UPDATE_FILE)
        self.download_thread.progressChanged.connect(self.update_progress)
        self.download_thread.downloadFinished.connect(
            self.on_download_finished)
        self.download_thread.start()

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)

    def on_download_finished(self):
        self.update_status.setText('Status: Unpacking...')
        self.extract_archive(
            LOCAL_UPDATE_FILE,
            os.path.join(
                self.game_path,
                'MO2/mods/RFAD_PATCH'))
        self.update_status.setText('Status: Update complete')
        self.progress_bar.setValue(100)

        # Заменяем локальный файл version.txt на новый
        try:
            new_version_path = os.path.join(
                self.game_path, REMOTE_VERSION_FILE)
            local_version_path = os.path.join(
                self.game_path, 'MO2/mods/RFAD_PATCH', LOCAL_VERSION_FILE)
            shutil.copyfile(new_version_path, local_version_path)
            logger.info(
                f"Local version file replaced with new version: {local_version_path}")
        except Exception as e:
            self.update_status.setText(
                f'Status: Error replacing version file: {
                    str(e)}')
            logger.error(f"Error replacing version file: {str(e)}")

    # def play_game(self):
    #     if not self.game_path:
    #         self.update_status.setText('Status: No game path set')
    #         return
    #
    #     game_executable = os.path.join(self.game_path, 'Skyrim.exe')
    #     if os.path.exists(game_executable):
    #         subprocess.Popen(game_executable, shell=True)
    #         self.update_status.setText('Status: Game started')
    #     else:
    #         self.update_status.setText('Status: Skyrim.exe not found')

    def get_drive_files(self):
        results = service.files().list(
            q=f"'{FOLDER_ID}' in parents",
            pageSize=10,
            fields="files(id, name, mimeType)").execute()
        return results.get('files', [])

    def extract_archive(self, archive_path, extract_to):
        if archive_path.endswith('.7z'):
            with py7zr.SevenZipFile(archive_path, mode='r') as z:
                z.extractall(extract_to)
        elif archive_path.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as z:
                z.extractall(extract_to)
        else:
            raise ValueError("Unsupported archive format")
        logger.info(f"Extracted archive {archive_path} to {extract_to}")

    def update_ui(self):
        QApplication.processEvents()  # Принудительное обновление интерфейса


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(style_qss)
    launcher = SkyrimLauncher()
    launcher.show()
    sys.exit(app.exec_())
