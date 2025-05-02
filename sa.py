import scratchattach as sa
import os
from modules import db_change as db

# --------------------- ScratchAttach ---------------------
project_id = 000000
session = sa.login("username", os.getenv('SCRATCH_PS'))
cloud = session.connect_cloud(project_id)
client = cloud.requests(used_cloud_vars=["1‎", "2‎", "3‎", "4‎"])

# --------------------- Init DB ---------------------
db.init_databases()

# --------------------- Scratch Requests ---------------------
@client.request
def balance(user):
    user = db.fix_name(user)
    if user not in db.db:
        db.set_balance(user, 100.0)
    return db.get_balance(user)

@client.request
def give(amount, users):
    try:
        amount = float(amount)
        recipient, sender = map(db.fix_name, users.split(" ", 1))
        if db.db.get(sender, 0) >= amount and amount > 0:
            db.set_balance(sender, db.db[sender] - amount)
            db.set_balance(recipient, db.db.get(recipient, 100.0) + amount)
            ts = db.generate_readable_timestamp()
            db.update_notifications(sender, f"{ts} - You gave {amount} Gems to {recipient}!")
            db.update_notifications(recipient, f"{ts} - {sender} gave you {amount} Gems")
            user = session.connect_user(recipient)
            user.post_comment(f"@{sender} gave you {amount} Gems in ScratchGems https://scratch.mit.edu/projects/1134723891")
            db.save_transaction(sender, recipient, amount)
            return db.get_balance(sender)
        return "Insufficient balance."
    except Exception:
        return "Invalid request."

@client.request
def search(user):
    user = db.fix_name(user)
    if user in db.db:
        return f"{user} has {db.get_balance(user)} Gems!"
    return f"{user}'s balance couldn't be found."

@client.request
def leaderboard():
    top = sorted(db.db.items(), key=lambda x: x[1], reverse=True)[:10]
    return [f"{k}: {int(v)}" for k, v in top]

@client.request
def notifications(user):
    user = db.fix_name(user)
    return db.notifications_db.get(user, ["No notifications!"])

@client.request
def change_balance(user, amount):
    db.set_balance(user, float(amount))
    return "success!"

@client.request
def get_preferences(user):
    return list(db.preferences_db.get(db.fix_name(user), {"theme": "blue", "mute": "False"}).values())

@client.request
def set_preferences(theme, user):
    db.update_preferences(user, {"theme": theme, "mute": "False"})
    return "updated preferences"

@client.event
def on_ready():
    print("ScratchAttach request handler is running")

# --------------------- Run ---------------------
if __name__ == '__main__':
    client.start(thread=True)
