from flask import Flask, jsonify, request, Blueprint
from datetime import datetime
from modules import db_change as db

# Initialize Flask app
bp = Blueprint('api', __name__) 

# Initialize databases
db.init_databases()

@bp.route('/')
def home():
    return jsonify({
        "version": "v1",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "docs": "/docs",
        "user_count": len(db.db),
        "total_balance": round(sum(db.db.values()))
    })

@bp.route('/users', methods=['GET'])
def get_users():
    return jsonify({"users": list(db.db.keys())})

@bp.route('/balances', methods=['GET'])
def get_balances():
    return jsonify({k: round(v) for k, v in db.db.items()})

@bp.route('/users/<username>', methods=['GET'])
def get_user(username):
    user = db.fix_name(username)
    if user not in db.db:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"username": user, "balance": db.get_balance(user)})

@bp.route('/verify')
def verify():
    return jsonify({"verification": "api-verified-v1"})

@bp.route('/transactions', methods=['GET'])
def get_all_transactions():
    return jsonify({"transactions": list(db.transactions_db.values())})

@bp.route('/transactions/<username>', methods=['GET'])
def get_user_transactions(username):
    user = db.fix_name(username)
    filtered = [
        tx for tx in db.transactions_db.values()
        if db.fix_name(tx["from"]) == user or db.fix_name(tx["to"]) == user
    ]
    return jsonify({"transactions": filtered})

@bp.route('/notifications/<username>', methods=['GET'])
def get_notifications(username):
    user = db.fix_name(username)
    return jsonify({"notifications": db.notifications_db.get(user, ["No notifications!"])})

@bp.route('/docs')
def docs():
    try:
        return open("docs.html").read()
    except FileNotFoundError:
        return jsonify({"error": "Documentation not found."}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
