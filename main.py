import sys
import os
import io
import threading
import logging
import time
import subprocess
import zipfile
import py7zr
import shutil
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QProgressBar
from PyQt5.QtGui import QPixmap, QPalette, QBrush
from PyQt5.QtCore import Qt, pyqtSignal, QThread

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
credentials = service_account.Credentials.from_service_account_info(credentials_info)
service = build('drive', 'v3', credentials=credentials)

FOLDER_ID = '1-ZJfs05U-aTmu2saVtdJQn3GibxzXQbo'
LOCAL_VERSION_FILE = 'version.txt'
LOCAL_UPDATE_FILE = 'update.7z'
CONFIG_FILE = 'config.txt'

logging.basicConfig(level=logging.INFO, filename='launcher.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

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
                time.sleep(0.05)
        self.downloadFinished.emit()

class SkyrimLauncher(QWidget):
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        # Определение пути к папке с игрой (текущая директория)
        self.game_path = os.path.abspath(os.getcwd())
        self.selected_game_folder.setText(f'Game folder: {self.game_path}')

        # Автоматическая проверка обновлений при запуске
        self.check_for_updates()

    def initUI(self):
        self.setWindowTitle('Skyrim Game Launcher')
        self.setGeometry(100, 100, 400, 300)

        # Установка фонового изображения
        background = QPixmap('assets/background.jpg')
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(background.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)))
        self.setPalette(palette)

        layout = QVBoxLayout()

        self.title = QLabel('Skyrim Game Launcher', self)
        self.title.setObjectName('title')
        layout.addWidget(self.title)

        self.selected_game_folder = QLabel('Game folder: None', self)
        layout.addWidget(self.selected_game_folder)

        self.update_status = QLabel('Status: Checking for updates...', self)
        layout.addWidget(self.update_status)

        self.local_version = QLabel('Local Version: N/A', self)
        layout.addWidget(self.local_version)

        self.online_version = QLabel('Online Version: N/A', self)
        layout.addWidget(self.online_version)

        self.update_button = QPushButton('Update', self)
        self.update_button.setVisible(False)
        self.update_button.clicked.connect(self.start_update)
        layout.addWidget(self.update_button)

        self.play_button = QPushButton('Play', self)
        self.play_button.clicked.connect(self.play_game)
        layout.addWidget(self.play_button)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def resizeEvent(self, event):
        background = QPixmap('assets/background.jpg')
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(background.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)))
        self.setPalette(palette)

    def check_for_updates(self):
        if not self.game_path:
            self.update_status.setText('Status: No game path set')
            return

        files = self.get_drive_files()
        version_file = next((f for f in files if f['mimeType'] == 'application/vnd.google-apps.document'), None)
        update_file = next((f for f in files if f['mimeType'] in ['application/x-7z-compressed', 'application/x-zip-compressed']), None)

        if not version_file or not update_file:
            self.update_status.setText('Status: Required files not found on Google Drive')
            return

        local_version_path = os.path.join(self.game_path, 'MO2/mods/RFAD_PATCH', LOCAL_VERSION_FILE)

        # Скачиваем файл версии
        self.download_file(service, version_file['id'], 'remote_version.txt', version_file['mimeType'])

        # Читаем локальную и удаленную версии
        with open(local_version_path, 'r') as file:
            local_version = file.read().strip()

        with open('remote_version.txt', 'r', encoding='utf-8-sig') as file:
            remote_version = file.read().strip()

        self.local_version.setText(f'Local Version: {local_version}')
        self.online_version.setText(f'Online Version: {remote_version}')

        if local_version != remote_version:
            self.update_status.setText('Status: Update available')
            self.update_button.setVisible(True)
        else:
            self.update_status.setText('Status: Up to date')
            self.update_button.setVisible(False)

    def start_update(self):
        if not self.game_path:
            self.update_status.setText('Status: No game path set')
            return
        
        files = self.get_drive_files()
        update_file = next((f for f in files if f['mimeType'] in ['application/x-7z-compressed', 'application/x-zip-compressed']), None)
        if not update_file:
            self.update_status.setText('Status: Update file not found')
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Запуск загрузки в отдельном потоке
        self.download_thread = DownloadThread(service, update_file['id'], LOCAL_UPDATE_FILE)
        self.download_thread.progressChanged.connect(self.update_progress)
        self.download_thread.downloadFinished.connect(self.on_download_finished)
        self.download_thread.start()

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)

    def on_download_finished(self):
        self.update_status.setText('Status: Unpacking...')
        self.extract_archive(LOCAL_UPDATE_FILE, os.path.join(self.game_path, 'MO2/mods/RFAD_PATCH'))
        self.update_status.setText('Status: Update complete')
        self.progress_bar.setValue(100)

        # Заменяем локальный файл версии на скачанный
        try:
            remote_version_path = os.path.join(self.game_path, 'MO2/mods/RFAD_PATCH', LOCAL_VERSION_FILE)
            shutil.copyfile('remote_version.txt', remote_version_path)
            logging.info(f"Local version file replaced with new version: {remote_version_path}")
        except Exception as e:
            self.update_status.setText(f'Status: Error replacing version file: {str(e)}')

    def play_game(self):
        if not self.game_path:
            self.update_status.setText('Status: No game path set')
            return

        game_executable = os.path.join(self.game_path, 'Skyrim.exe')
        if os.path.exists(game_executable):
            subprocess.Popen(game_executable, shell=True)
            self.update_status.setText('Status: Game started')
        else:
            self.update_status.setText('Status: Skyrim.exe not found')

    def download_file(self, service, file_id, destination, mime_type=None):
        if mime_type == 'application/vnd.google-apps.document':  # Проверяем, является ли файл Google Docs
            request = service.files().export_media(fileId=file_id, mimeType='text/plain')
        else:
            request = service.files().get_media(fileId=file_id)
        
        fh = io.FileIO(destination, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        
        while not done:
            status, done = downloader.next_chunk()
            if status:
                logging.info(f"Загрузка {int(status.progress() * 100)}%.")
        fh.close()
        
        logging.info(f"Файл {destination} успешно загружен.")

    def get_drive_files(self):
        results = service.files().list(q=f"'{FOLDER_ID}' in parents", pageSize=10, fields="files(id, name, mimeType)").execute()
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
        logging.info(f"Extracted archive {archive_path} to {extract_to}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(style_qss)
    launcher = SkyrimLauncher()
    launcher.show()
    sys.exit(app.exec_())
