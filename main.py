import atexit
import sys
import os
import io
import logging
import subprocess
import tempfile
import zipfile
import threading
import webbrowser
from functools import partial

import shutil
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar, QHBoxLayout, QGridLayout, QStackedWidget
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QFontDatabase, QCursor, QPainter, QColor, QLinearGradient
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer, QSize, QRectF

# Встроенное содержимое style.qss
style_qss = """
QLabel#title {
    color: white;
    font-size: 36px;
    font-weight: bold;
    text-align: center;
    font-family: 'Magic Cards Cyrillic';
}

QVBoxLayout {
    margin-left: 300px;
}

QToolTip { 
    background-color: white; 
    color: black;
    font-weight: bold;
    font-size: 16px;
    padding: 7px;
}

QLabel {
    color: white;
    font-size: 32px;
    margin-right: 10px;
    font-family: 'Magic Cards Cyrillic';
}

QProgressBar {
    background: rgb(157,127,109);
    background: linear-gradient(90deg, rgba(157,127,109,1) 0%, rgba(194,171,127,1) 100%);
    border-radius: 5px;
    text-align: center;
}

QProgressBar::chunk {
    background: rgb(117,154,174);
    background: linear-gradient(90deg, rgba(117,154,174,1) 0%, rgba(83,101,136,1) 100%);
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

#FOLDER_ID = '1-ZJfs05U-aTmu2saVtdJQn3GibxzXQbo' # dev folder
FOLDER_ID = '1JUOctbsugh2IIEUCWcBkupXYVYoJMg4G' # refrain folder
LOCAL_VERSION_FILE = 'version.txt'
REMOTE_VERSION_FILE = 'remote_version.txt'
LOCAL_UPDATE_FILE = 'update.zip'

logging.basicConfig(level=logging.INFO, filename='launcher.log', format='%(asctime)s - %(levelname)s - %(message)s')


def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS  # noqa
    else:
        base_path = os.path.dirname(__file__)

    return os.path.join(base_path, relative_path)


def open_link(link: str) -> None:
    browser = webbrowser.get()
    browser.open_new_tab(link)


def launch_application(app_path: str) -> None:
    if os.path.exists(app_path):
        os.chdir(app_path)
        subprocess.Popen("ModOrganizer.exe", shell=True)
    else:
        logging.error(f"Приложение не найдено: {app_path}")


def open_explorer(path: str) -> None:
    if os.path.exists(path):
        subprocess.Popen(f'explorer "{path}"', shell=True)
    else:
        logging.error(f"Путь не найден: {path}")


class VersionCheckThread(QThread):
    versionCheckCompleted = pyqtSignal(str, str)

    def __init__(self, service, game_path):
        super().__init__()
        self.service = service
        self.game_path = game_path

    def run(self):
        files = self.get_drive_files()
        version_file = next(
            (f for f in files if f['name'] == 'version'),
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
        try:
            with open(local_version_path, 'r', encoding='utf-8') as file:
                local_version = file.read().strip()
        except FileNotFoundError:
            local_version = "Not found"
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
            downloader = MediaIoBaseDownload(fh, request, chunksize=100 * 1024 * 1024)

            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    self.progressChanged.emit(progress)
                    QApplication.processEvents()  # Обновляем интерфейс
        self.downloadFinished.emit()
        
        
class RoundedProgressBar(QProgressBar):
    def __init__(self, *args, **kwargs):
        super(RoundedProgressBar, self).__init__(*args, **kwargs)
        self.setTextVisible(True)  # Скрыть текст

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        radius = 5
        painter.setBrush(QColor("#1A1A1A"))
        painter.drawRoundedRect(rect, radius, radius)

        fill_rect = QRectF(rect.x(), rect.y(), rect.width() * (self.value() / self.maximum()), rect.height())

        # Градиент для заполненной части
        gradient = QLinearGradient(fill_rect.topLeft(), fill_rect.topRight())
        gradient.setColorAt(0, QColor(157, 127, 109))
        gradient.setColorAt(1, QColor(194, 171, 127))

        painter.setBrush(gradient)
        painter.drawRoundedRect(fill_rect, radius, radius)


class SkyrimLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        # Определение пути к папке с игрой (текущая директория)
        self.game_path = os.path.abspath(os.getcwd())
        #  Определение пути до profile
        self.path_to_profile = os.path.join(self.game_path, 'MO2/profiles/RFAD')

        # Асинхронная проверка обновлений после отображения окна
        self.check_updates_async()

        # Таймер для обновления интерфейса
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(100)  # Обновление каждые 100 мс

    def initUI(self):
        self.setWindowTitle('RFAD Game Launcher')
        self.setGeometry(100, 100, 1058, 638)

        layout = QVBoxLayout()

        self.game_path = os.path.abspath(os.getcwd())
        # Заголовок "RFAD"
        header_pixmap = QPixmap(resource_path('assets/Header.svg'))
        self.title = QLabel(self)
        self.title.setPixmap(header_pixmap)
        self.title.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.title)

        # Кнопки Play, Update, Exit по центру
        btn_layout = QGridLayout()
        btn_layout.setSpacing(20)
        btn_layout.setContentsMargins(0, 15, 0, 20)
        btn_layout.setAlignment(Qt.AlignCenter)
        self.play_button = self.add_svg_button(btn_layout, 0, 'assets/options/Play.svg', self.play_game)
        self.update_button = self.add_svg_button(btn_layout, 1, 'assets/options/Update.svg', self.start_update)
        self.disable_update_button()  # По умолчанию кнопка заблокирована
        self.exit_button = self.add_svg_button(btn_layout, 2, 'assets/options/Exit.svg', lambda _: sys.exit(0))
        layout.addLayout(btn_layout)

        # Прогресс-бар
        self.progress_bar = RoundedProgressBar(self)
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedWidth(635)
        self.progress_bar.setFixedHeight(10)

        progress_label = QLabel(self)
        progress_pixmap = QPixmap(resource_path('assets/ProgressBar.svg'))
        progress_label.setPixmap(progress_pixmap)
        progress_label.setAlignment(Qt.AlignCenter)
        progress_label.setAttribute(Qt.WA_TranslucentBackground)
        progress_label.setFixedHeight(30)

        q = QHBoxLayout()
        q.addWidget(self.progress_bar)
        progress_label.setLayout(q)
        layout.addWidget(progress_label)

        # Версии и статус обновлений внизу по центру
        text_layout = QGridLayout()
        status_layout = QHBoxLayout()
        text_layout.setSpacing(0)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setAlignment(Qt.AlignCenter)
        status_layout.setAlignment(Qt.AlignCenter)
        self.update_status = QLabel('Status: Checking for updates...', self)
        status_layout.addWidget(self.update_status)
        status_layout.setContentsMargins(90, 0, 0, 0)
        text_layout.addLayout(status_layout, 0, 0)

        vesrion_layout = QHBoxLayout()
        self.local_version = QLabel('Local Version: N/A', self)
        self.online_version = QLabel('Last Version: N/A', self)
        vesrion_layout.addWidget(self.local_version)
        vesrion_layout.addWidget(self.online_version)
        text_layout.addLayout(vesrion_layout, 1, 0)
        layout.addLayout(text_layout)

        # Иконки соцсетей внизу
        footer_layout = QVBoxLayout()  # Изменено на QVBoxLayout для добавления текста под кнопками
        footer_buttons_layout = QGridLayout()
        footer_buttons_layout.setColumnStretch(5, 1)
        footer_buttons_layout.setSpacing(18)
        footer_buttons_layout.setContentsMargins(0, 0, 0, 0)

        # Кнопка Patreon
        self.add_footer_button(footer_buttons_layout, 0, 'assets/buttons/Patreon.svg', "Patreon",
                               lambda: open_link("https://www.patreon.com/RFaD_ChickenEdition/membership"))

        # Кнопка Discord
        self.add_footer_button(footer_buttons_layout, 1, 'assets/buttons/Discord.svg', "Discord",
                               lambda: open_link("https://discord.gg/q2ygjdk8Gv"))

        # Кнопка MO2
        mo2_path = os.path.join(self.game_path, 'MO2')
        self.add_footer_button(footer_buttons_layout, 2, 'assets/buttons/MO2.svg', "MO",
                               lambda: launch_application(mo2_path))

        # Кнопка GameFolder
        self.add_footer_button(footer_buttons_layout, 3, 'assets/buttons/GameFolder.svg', "Каталог",
                               lambda: open_explorer(self.game_path))

        # Кнопка DataBase
        self.add_footer_button(footer_buttons_layout, 4, 'assets/buttons/DataBase.svg', "Знания", lambda: open_link(
            "https://docs.google.com/spreadsheets/d/1XsKJBINxQxzXa2TtUoSLqt1Kp0-03Sz2tZ65PlJY94M/edit?gid=1184182319#gid=1184182319&range=A1"))

        # Кнопка Boosty
        self.add_footer_button(footer_buttons_layout, 5, 'assets/buttons/Boosty.svg', "Boosty",
                               lambda: open_link("https://boosty.to/skyrim_rfad_chicken"))

        footer_buttons_layout.setAlignment(Qt.AlignCenter)
        footer_layout.addLayout(footer_buttons_layout)

        layout.addLayout(footer_layout)

        self.setLayout(layout)

        # Загрузка шрифта
        font_id = QFontDatabase.addApplicationFont(resource_path('assets/MagicCardsCyrillic/MagicCardsCyrillic.ttf'))
        if font_id == -1:
            logging.error("Не удалось загрузить шрифт 'Magic Cards Cyrillic'")
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            self.setStyleSheet(style_qss)

    def add_footer_button(self, layout, place, svg_path, description, click_action):
        """Добавляет кнопку футера с описанием под ней."""
        vbox = QVBoxLayout()
        button = QLabel(self)
        button.setPixmap(QPixmap(resource_path(svg_path)))
        button.setFixedSize(QSize(100, 100))
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.mousePressEvent = lambda event: click_action()  # Используем lambda для корректного вызова
        button.setAlignment(Qt.AlignCenter)
        button.setToolTip(description)
        button.resize(button.sizeHint())

        vbox.addWidget(button)
        #vbox.addWidget(label)
        vbox.setAlignment(Qt.AlignCenter)
        layout.addWidget(button, 0, place, 1, 1)

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

    def add_svg_button(self, layout, place, svg_path, click_action):
        """Добавляет SVG как кнопку с заданным действием по клику."""
        button = QLabel(self)
        button.setPixmap(QPixmap(resource_path(svg_path)))
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.mousePressEvent = click_action
        button.setAlignment(Qt.AlignCenter)
        layout.addWidget(button, place, 0)
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
        self.online_version.setText(f'Last Version: {remote_version}')

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

    def update_modlist(self):
        path_to_file = os.path.join(self.path_to_profile, 'modlist.txt')
        with open(path_to_file, 'r+', encoding='utf-8') as f:
            new_modlist = '+RFAD_PATCH\n' + f.read().replace("+RFAD_PATCH\n", "")
            f.seek(0)
            f.write(new_modlist)
            f.truncate()

    @staticmethod
    def update_order(path_to_file: str, new_list: str, separator: str):
        with open(path_to_file, 'r+', encoding='utf-8') as f:
            loadorder = f.read()
            head, tail = loadorder.split(separator)
            if separator == "Requiem for the Indifferent.esp":
                mod_list = [f"{x}" for x in new_list.split("\n")]
            else:
                mod_list = [f"*{x}" for x in new_list.split("\n")]
            for x in mod_list:
                head = head.replace(x, "")
            new_list = "\n".join(mod_list)
            f.seek(0)
            f.write(head.rstrip() + '\n' + new_list + '\n' + separator + tail)
            f.truncate()

    def download_file(self, service, file_id, destination, mime_type=None):
        if mime_type == 'application/vnd.google-apps.document':
            request = service.files().export_media(fileId=file_id, mimeType='text/plain')
        else:
            request = service.files().get_media(fileId=file_id)

        fh = io.FileIO(destination, 'wb')
        downloader = MediaIoBaseDownload(fh, request)

        # Принудительно устанавливаем меньший размер буфера
        downloader._buffer_size = 100 * 1024 * 1024  # 1 MB для более частых обновлений
        done = False

        while not done:
            status, done = downloader.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                QApplication.processEvents()  # Обновляем интерфейс
        fh.close()

        logging.info(f"Файл {destination} успешно загружен.")

    def get_new_order(self) -> str | None:
        """"Новый порядок модов из скачанного файла"""
        files = self.get_drive_files()
        modlist_file = next(
            (f for f in files if f['name'] == 'modlist'),
            None)
        self.download_file(
            service,
            modlist_file['id'],
            'modlist.txt',
            modlist_file['mimeType'])
        with open('modlist.txt', 'r', encoding='utf-8-sig') as file:
            modlist = file.read().strip()
            return modlist

    def on_download_finished(self):
        self.update_status.setText('Status: Unpacking...')

        patch_path = os.path.join(self.game_path, 'MO2/mods/RFAD_PATCH')
        if not os.path.exists(patch_path):
            os.makedirs(patch_path)
        else:
            # Очистка папки перед распаковкой
            self.clean_patch_folder(patch_path, LOCAL_VERSION_FILE)

        thread = threading.Thread(target=self.extract_archive, args=(LOCAL_UPDATE_FILE, patch_path))
        thread.start()
        self.update_modlist()
        
        try:
            new_order = self.get_new_order()
            if new_order:
                self.update_order(path_to_file=os.path.join(self.path_to_profile, "plugins.txt"), new_list=new_order, separator="*Requiem for the Indifferent.esp")
                self.update_order(path_to_file=os.path.join(self.path_to_profile, "loadorder.txt"), new_list=new_order, separator="Requiem for the Indifferent.esp")
            self.update_status.setText('Status: Update complete')
            self.progress_bar.setValue(100)
        except Exception as e:
            error_text = f'Status: Error change loadorder: {str(e)}'
            self.update_status.setText(error_text)
            logging.error(f"Error change loadorder: {str(e)}")

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
        mo2_path = os.path.join(self.game_path, "MO2")
        if os.path.exists(mo2_path):
            os.chdir(mo2_path)
            subprocess.Popen("ModOrganizer.exe moshortcut://:SKSE", shell=True)
        #
        # game_executable = os.path.join(self.game_path, 'skse64_loader.exe')
        # if os.path.exists(game_executable):
        #     subprocess.Popen(game_executable, shell=True)
        #     self.update_status.setText('Status: Game started')
        # else:
        #     self.update_status.setText('Status: skse64_loader.exe not found')

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

# Временный фикс чтоб не копилось
def del_temp_dirs():
    root_dir = tempfile.gettempdir()
    for entry in os.listdir(root_dir):
        path = os.path.join(root_dir, entry)
        if os.path.isdir(path) and entry.startswith('_MEI'):
            try:
                shutil.rmtree(path)
            except Exception as  e:
                logging.error(f"Error: {e}")


if __name__ == '__main__':
    atexit.register(del_temp_dirs)
    app = QApplication(sys.argv)
    app.setStyleSheet(style_qss)
    launcher = SkyrimLauncher()
    launcher.show()
    sys.exit(app.exec_())

