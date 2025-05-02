import base64
import os
import time
import requests
from datetime import datetime

# GitHub repo configuration
GITHUB_API_KEY = os.getenv('GH_KEY')
REPO_OWNER = "SnoopCoinScratch"
REPO_NAME = "SnoopCoin-V2"
BRANCH = "main"
HEADERS = {
    "Authorization": f"token {GITHUB_API_KEY}",
    "Accept": "application/vnd.github+json"
}

# File SHA values for GitHub
sha_db = None
sha_notifs = None
sha_tx = None
sha_prefs = None

# In-memory databases
db = {}
notifications_db = {}
transactions_db = {}
preferences_db = {}

def github_file_path(name):
    return f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/db/{name}.txt"

def github_load(name):
    url = github_file_path(name)
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 404:
            print(f"{name}.txt not found on GitHub. Starting fresh.")
            return {}, None
        res.raise_for_status()
        content = res.json()
        remote_data = eval(base64.b64decode(content["content"]).decode())
        return remote_data, content["sha"]
    except Exception as e:
        print(f"Failed to load {name} from GitHub. Error: {e}")
        return {}, None

def github_save(name, local_data, sha=None):
    url = github_file_path(name)
    raw = repr(local_data).encode()
    b64 = base64.b64encode(raw).decode()
    payload = {
        "message": f"update {name}",
        "content": b64,
        "branch": BRANCH
    }
    if sha:
        payload["sha"] = sha
    try:
        res = requests.put(url, headers=HEADERS, json=payload)
        res.raise_for_status()
        return res.json()["content"]["sha"]
    except Exception as e:
        print(f"Failed to save {name} to GitHub. Error: {e}")
        return sha

def init_databases():
    global db, sha_db, notifications_db, sha_notifs, transactions_db, sha_tx, preferences_db, sha_prefs
    db, sha_db = github_load("dict_balances")
    notifications_db, sha_notifs = github_load("dict_notifications")
    transactions_db, sha_tx = github_load("dict_transactions")
    preferences_db, sha_prefs = github_load("dict_preferences")

def fix_name(name):
    return name.replace(" ", "").replace("@", "").lower()

def set_balance(user, amount):
    global sha_db
    user = fix_name(user)
    db[user] = float(amount)
    sha_db = github_save("dict_balances", db, sha_db)

def get_balance(user):
    return round(db.get(fix_name(user), 100.0))

def save_transaction(sender, receiver, amount):
    global sha_tx
    tx_id = f"{int(time.time())}_{sender}"
    transactions_db[tx_id] = {
        "timestamp": int(time.time()),
        "id": tx_id,
        "from": sender,
        "to": receiver,
        "amount": amount
    }
    sha_tx = github_save("dict_transactions", transactions_db, sha_tx)

def update_notifications(user, message):
    global sha_notifs
    user = fix_name(user)
    notifs = notifications_db.get(user, [])
    notifs.append(message)
    notifications_db[user] = notifs
    sha_notifs = github_save("dict_notifications", notifications_db, sha_notifs)

def update_preferences(user, prefs):
    global sha_prefs
    user = fix_name(user)
    preferences_db[user] = prefs
    sha_prefs = github_save("dict_preferences", preferences_db, sha_prefs)

def generate_readable_timestamp():
    return datetime.now().strftime("%H:%M on %m/%d/%y")
