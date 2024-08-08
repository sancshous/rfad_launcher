import os
import io
import eel
import threading
import logging
import time
import subprocess
import zipfile
import py7zr
import shutil
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from tkinter import Tk
from tkinter.filedialog import askdirectory

# Инициализация API Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = 'credentials.json'
credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)

FOLDER_ID = '1-ZJfs05U-aTmu2saVtdJQn3GibxzXQbo'
LOCAL_VERSION_FILE = 'version.txt'
LOCAL_UPDATE_FILE = 'update.7z'
CONFIG_FILE = 'config.txt'

logging.basicConfig(level=logging.INFO, filename='launcher.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

eel.init('web')

def get_saved_game_path():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return file.read().strip()
    return None

def save_game_path(path):
    with open(CONFIG_FILE, 'w') as f:
        f.write(path)

def get_drive_files():
    results = service.files().list(
        q=f"'{FOLDER_ID}' in parents",
        fields="files(id, name, mimeType)").execute()
    files = results.get('files', [])
    return files

def download_file(service, file_id, destination, mime_type=None):
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
            eel.update_status({'status': 'Downloading', 'progress': int(status.progress() * 100)})
            eel.sleep(0.1)  # Обновляем интерфейс
    fh.close()
    
    logging.info(f"Файл {destination} успешно загружен.")

@eel.expose
def choose_game_folder():
    def folder_selection():
        logging.info("Choosing game folder...")
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)  # Принудительно выводим окно на передний план
        folder_selected = askdirectory()
        root.destroy()  # Закрываем окно после выбора папки
        
        if folder_selected:
            save_game_path(folder_selected)
            logging.info(f"Selected game folder: {folder_selected}")
        else:
            logging.info("No folder selected.")
        
        eel.set_folder_path(folder_selected)  # Передаем результат в JavaScript

    threading.Thread(target=folder_selection).start()

@eel.expose
def set_folder_path(path):
    pass

@eel.expose
def check_for_updates():
    game_path = get_saved_game_path()
    if not game_path:
        return {'status': 'No game path set'}

    files = get_drive_files()
    version_file = next((f for f in files if f['mimeType'] == 'application/vnd.google-apps.document'), None)
    update_file = next((f for f in files if f['mimeType'] in ['application/x-7z-compressed', 'application/x-zip-compressed']), None)
    
    if not version_file or not update_file:
        return {'status': 'Required files not found on Google Drive'}
    
    local_version_path = os.path.join(game_path, 'MO2/mods/RFAD_PATCH', LOCAL_VERSION_FILE)

    # Скачиваем файл версии
    download_file(service, version_file['id'], 'remote_version.txt', version_file['mimeType'])

    # Читаем локальную и удаленную версии
    with open(local_version_path, 'r') as file:
        local_version = file.read().strip()

    with open('remote_version.txt', 'r', encoding='utf-8-sig') as file:
        remote_version = file.read().strip()

    if local_version != remote_version:
        return {'status': 'Update available', 'local_version': local_version, 'online_version': remote_version, 'update_file_id': update_file['id']}
    else:
        return {'status': 'Up to date', 'local_version': local_version, 'online_version': remote_version}

@eel.expose
def start_update(update_file_id):
    def update_process():
        game_path = get_saved_game_path()
        if not game_path:
            eel.update_status({'status': 'No game path set'})
            eel.sleep(0.1)
            return
        
        download_path = os.path.join(game_path, 'MO2/mods/RFAD_PATCH')
        eel.update_status({'status': 'Downloading...', 'progress': 0})
        eel.sleep(0.1)

        try:
            download_file(service, update_file_id, LOCAL_UPDATE_FILE)
        except Exception as e:
            eel.update_status({'status': f'Error during download: {str(e)}'})
            return
        
        eel.update_status({'status': 'Unpacking...', 'progress': 0})
        eel.sleep(0.1)

        try:
            extract_archive(LOCAL_UPDATE_FILE, download_path)
            eel.update_status({'status': 'Update complete', 'progress': 100})
        except Exception as e:
            eel.update_status({'status': f'Error: {str(e)}'})
            return

        # Заменяем локальный файл версии на скачанный
        try:
            remote_version_path = os.path.join(download_path, LOCAL_VERSION_FILE)
            shutil.copyfile('remote_version.txt', remote_version_path)
            logging.info(f"Local version file replaced with new version: {remote_version_path}")
        except Exception as e:
            eel.update_status({'status': f'Error replacing version file: {str(e)}'})
            return

        eel.update_status({'status': 'Update successful. Version file replaced.'})

    threading.Thread(target=update_process).start()


def extract_archive(file_path, extract_to):
    try:
        if file_path.endswith('.7z'):
            try:
                with py7zr.SevenZipFile(file_path, mode='r') as z:
                    z.extractall(extract_to)
                logging.info('7z archive extracted.')
            except py7zr.exceptions.UnsupportedCompressionMethodError as e:
                logging.warning(f"Unsupported method by py7zr: {e}. Trying 7z command line tool.")
                subprocess.run(['7z', 'x', file_path, f'-o{extract_to}'], check=True)
                logging.info('7z archive extracted using command line.')
        elif file_path.endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            logging.info('ZIP archive extracted.')
        else:
            raise ValueError("Unsupported archive format.")
    except Exception as e:
        logging.error(f"Error during unpacking: {e}")
        raise

@eel.expose
def play_game():
    game_path = get_saved_game_path()
    if not game_path:
        eel.update_status({'status': 'No game path set'})
        return
    
    game_executable = os.path.join(game_path, 'Skyrim.exe')
    if os.path.exists(game_executable):
        subprocess.Popen(game_executable, shell=True)
        eel.update_status({'status': 'Game started'})
    else:
        eel.update_status({'status': 'Game executable not found'})

eel.start('index.html', size=(800, 600))
