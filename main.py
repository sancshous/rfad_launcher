import sys
import os
import io
import logging
import subprocess
import zipfile
import webbrowser
from functools import partial

import shutil
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar, QHBoxLayout
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QFontDatabase, QCursor
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer, QSize

# Встроенное содержимое style.qss
style_qss = """
QLabel#title {
    color: white;
    font-size: 36px;
    font-weight: bold;
    text-align: center;
    font-family: 'Magic Cards Cyrillic';
}

QLabel {
    color: white;
    font-size: 24px;
    font-family: 'Magic Cards Cyrillic';
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
LOCAL_UPDATE_FILE = 'update.zip'

logging.basicConfig(level=logging.INFO, filename='launcher.log', filemode='w',
                    format='%(asctime)s - %(levellevelname)s - %(message)s')


def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)

    return os.path.join(base_path, relative_path)


FOOTER_BUTTONS_ICONS = [
    (resource_path("assets/buttons/Patreon.svg"), "https://www.patreon.com/RFaD_ChickenEdition/membership"),
    #(resource_path("assets/buttons/Discord.svg"), "https://discord.gg/q2ygjdk8Gv"),
    (resource_path("assets/buttons/MO2.svg"), "https://boosty.to/skyrim_rfad_chicken"),
    (resource_path("assets/buttons/GameFolder.svg"), "https://boosty.to/skyrim_rfad_chicken"),
    #(resource_path("assets/buttons/DataBase.svg"), "https://docs.google.com/spreadsheets/d/1XsKJBINxQxzXa2TtUoSLqt1Kp0-03Sz2tZ65PlJY94M/edit?gid=1184182319#gid=1184182319&range=A1"),
    (resource_path("assets/buttons/Boosty.svg"), "https://boosty.to/skyrim_rfad_chicken"),
]


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

        with open(local_version_path, 'r', encoding='utf-8') as file:
            local_version = file.read().strip()

        with open('remote_version.txt', 'r', encoding='utf-8') as file:
            remote_version = file.read().strip()

        self.versionCheckCompleted.emit(local_version, remote_version)

    def download_file(self, service, file_id, destination, mime_type=None):
        if mime_type == 'application/vnd.google-apps.document':
            request = service.files().export_media(fileId=file_id, mimeType='text/plain')
        else:
            request = service.files().get_media(fileId=file_id)

        fh = io.FileIO(destination, 'wb')
        downloader = MediaIoBaseDownload(fh, request)

        # Принудительно устанавливаем меньший размер буфера
        downloader._buffer_size = 1024 * 1024  # 1 MB для более частых обновлений
        done = False

        while not done:
            status, done = downloader.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                QApplication.processEvents()  # Обновляем интерфейс
        fh.close()

        logging.info(f"Файл {destination} успешно загружен.")

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

            # Принудительно устанавливаем меньший размер буфера
            downloader._buffer_size = 1024 * 1024  # 1 MB для более частых обновлений
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    self.progressChanged.emit(progress)
                    QApplication.processEvents()  # Обновляем интерфейс
        self.downloadFinished.emit()


class SkyrimLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        # Определение пути к папке с игрой (текущая директория)
        self.game_path = os.path.abspath(os.getcwd())

        # Асинхронная проверка обновлений после отображения окна
        self.check_updates_async()

        # Таймер для обновления интерфейса
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(100)  # Обновление каждые 100 мс

    def initUI(self):
        self.setWindowTitle('RFAD Game Launcher')
        self.setGeometry(100, 100, 1024, 768)

        layout = QVBoxLayout()

        # Заголовок "RFAD"
        header_pixmap = QPixmap(resource_path('assets/Header.svg'))
        self.title = QLabel(self)
        self.title.setPixmap(header_pixmap)
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)

        # Кнопки Play, Update, Exit по центру
        self.update_button = self.add_svg_button(layout, 'assets/options/Play.svg', self.play_game)
        self.update_button = self.add_svg_button(layout, 'assets/options/Update.svg', self.start_update)
        self.disable_update_button()  # По умолчанию кнопка заблокирована
        self.exit_button = self.add_svg_button(layout, 'assets/options/Exit.svg', self.close)

        # Версии и статус обновлений внизу по центру
        version_layout = QHBoxLayout()
        self.local_version = QLabel('Local Version: N/A', self)
        self.online_version = QLabel('Online Version: N/A', self)
        version_layout.addWidget(self.local_version)
        version_layout.addWidget(self.online_version)
        version_layout.setAlignment(Qt.AlignCenter)
        layout.addLayout(version_layout)

        self.update_status = QLabel('Status: Checking for updates...', self)
        layout.addWidget(self.update_status)
        self.update_status.setAlignment(Qt.AlignCenter)

        # Прогресс-бар
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Иконки соцсетей внизу
        footer_layout = QHBoxLayout()
        for url_icon, link in FOOTER_BUTTONS_ICONS:
            button = QLabel(self)
            button.setPixmap(QPixmap(url_icon))
            button.setFixedSize(QSize(75, 75))
            button.setCursor(QCursor(Qt.PointingHandCursor))
            button.mousePressEvent = partial(self.open_link, link=link)
            footer_layout.addWidget(button)
        footer_layout.setAlignment(Qt.AlignCenter)
        layout.addLayout(footer_layout)

        self.setLayout(layout)

        # Загрузка шрифта
        font_id = QFontDatabase.addApplicationFont(resource_path('assets/MagicCardsCyrillic/MagicCardsCyrillic.ttf'))
        if font_id == -1:
            logging.error("Не удалось загрузить шрифт 'Magic Cards Cyrillic'")
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            self.setStyleSheet(style_qss)
            
    def update_background(self):
        # Установка фонового изображения
        pixmap = QPixmap(resource_path('assets/Body.svg'))
        palette = QPalette()
        palette.setBrush(
            QPalette.Background,
            QBrush(
                pixmap.scaled(
                    self.size(),
                    Qt.IgnoreAspectRatio,
                    Qt.SmoothTransformation)))
        self.setPalette(palette)
            
    def resizeEvent(self, event):
        self.update_background()
        super().resizeEvent(event)

    def add_svg_button(self, layout, svg_path, click_action):
        """Добавляет SVG как кнопку с заданным действием по клику."""
        button = QLabel(self)
        button.setPixmap(QPixmap(resource_path(svg_path)))
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.mousePressEvent = click_action
        button.setAlignment(Qt.AlignCenter)
        layout.addWidget(button)
        layout.setAlignment(button, Qt.AlignCenter)
        return button

    def disable_update_button(self):
        """Деактивировать кнопку Update."""
        self.update_button.setEnabled(False)
        self.update_button.setStyleSheet("opacity: 0.5;")

    def enable_update_button(self):
        """Активировать кнопку Update."""
        self.update_button.setEnabled(True)
        self.update_button.setStyleSheet("opacity: 1.0;")

    def open_link(self, event, link):
        open_link(link)

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

        self.local_version.setText(f'Local Version: {local_version}')
        self.online_version.setText(f'Online Version: {remote_version}')

        if local_version != remote_version:
            self.update_status.setText('Status: Update available')
            self.progress_bar.setVisible(True)
            self.enable_update_button()
        else:
            self.update_status.setText('Status: Up to date')
            self.progress_bar.setVisible(False)
            self.disable_update_button()

    def start_update(self, event=None):
        if not self.game_path:
            self.update_status.setText('Status: No game path set')
            return

        files = self.get_drive_files()
        update_file = next(
            (f for f in files if f['mimeType'] in [
                'application/x-zip-compressed']),
            None)
        if not update_file:
            self.update_status.setText('Status: Update file not found')
            return

        self.update_status.setText('Status: Downloading...')
        self.download_thread = DownloadThread(
            service, update_file['id'], LOCAL_UPDATE_FILE)
        self.download_thread.progressChanged.connect(self.update_progress)
        self.download_thread.downloadFinished.connect(
            self.on_download_finished)
        self.download_thread.start()

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)
        QApplication.processEvents()  # Обновление интерфейса

    def on_download_finished(self):
        self.update_status.setText('Status: Unpacking...')
        # Очистка папки перед распаковкой
        patch_path = os.path.join(self.game_path, 'MO2/mods/RFAD_PATCH')
        self.clean_patch_folder(patch_path, LOCAL_VERSION_FILE)

        self.extract_archive(
            LOCAL_UPDATE_FILE,
            patch_path)
        self.update_status.setText('Status: Update complete')
        self.progress_bar.setValue(100)

        # Заменяем локальный файл version.txt на новый
        try:
            new_version_path = os.path.join(
                self.game_path, REMOTE_VERSION_FILE)
            local_version_path = os.path.join(
                patch_path, LOCAL_VERSION_FILE)
            shutil.copyfile(new_version_path, local_version_path)
            logging.info(
                f"Local version file replaced with new version: {local_version_path}")
        except Exception as e:
            error_text = f'Status: Error replacing version file: {str(e)}'
            self.update_status.setText(error_text)
            logging.error(f"Error replacing version file: {str(e)}")

    def clean_patch_folder(self, folder_path, exclude_file):
        """Очистить папку, кроме указанного файла."""
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if item != exclude_file:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
        logging.info(f"Folder {folder_path} cleaned, except {exclude_file}.")

    def play_game(self, event=None):
        if not self.game_path:
            self.update_status.setText('Status: No game path set')
            return

        game_executable = os.path.join(self.game_path, 'skse64_loader.exe')
        if os.path.exists(game_executable):
            subprocess.Popen(game_executable, shell=True)
            self.update_status.setText('Status: Game started')
        else:
            self.update_status.setText('Status: skse64_loader.exe not found')

    def get_drive_files(self):
        results = service.files().list(
            q=f"'{FOLDER_ID}' in parents",
            pageSize=10,
            fields="files(id, name, mimeType)").execute()
        return results.get('files', [])

    def extract_archive(self, archive_path, extract_to):
        if archive_path.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as z:
                z.extractall(extract_to)
        else:
            raise ValueError("Unsupported archive format")
        logging.info(f"Extracted archive {archive_path} to {extract_to}")

    def update_ui(self):
        QApplication.processEvents()  # Принудительное обновление интерфейса


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(style_qss)
    launcher = SkyrimLauncher()
    launcher.show()
    sys.exit(app.exec_())
