let selectedGameFolderPath = '';

async function chooseGameFolder() {
    console.log("chooseGameFolder() called");
    await eel.choose_game_folder()();
}

eel.expose(set_folder_path);
function set_folder_path(folderPath) {
    console.log("Folder selected:", folderPath);
    if (folderPath) {
        document.getElementById('selected-game-folder').innerText = `Selected game folder: ${folderPath}`;
    } else {
        console.log("No folder selected.");
    }
}

async function checkForUpdates() {
    const status = await eel.check_for_updates()();
    document.getElementById('update-status').innerText = `Status: ${status.status}`;
    if (status.local_version) {
        document.getElementById('local-version').innerText = `Local Version: ${status.local_version}`;
    }
    if (status.online_version) {
        document.getElementById('online-version').innerText = `Online Version: ${status.online_version}`;
    }
    if (status.status === 'Update available') {
        document.getElementById('update-button').style.display = 'block';
        document.getElementById('update-button').onclick = () => startUpdate(status.update_file_id);
    } else {
        document.getElementById('update-button').style.display = 'none';
    }
}

eel.expose(update_status);
function update_status(status) {
    console.log("Status update received:", status);
    if (status && status.status) {
        document.getElementById('update-status').innerText = `Status: ${status.status}`;
    }
    if (status && status.progress !== undefined) {
        document.getElementById('progress-bar').value = status.progress;
    }
}

// Кнопка начала обновления
async function startUpdate(update_file_id) {
    console.log("Starting update...");
    await eel.start_update(update_file_id)();
}
