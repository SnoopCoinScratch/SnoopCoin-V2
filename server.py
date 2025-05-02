import os
import importlib
from flask import Flask

app = Flask(__name__)

EXCLUDED_FILES = {'build.py', 'server.py', '__init__.py'}

# Dynamically import and register blueprints from files in the same directory
current_dir = os.path.dirname(os.path.abspath(__file__))

for filename in os.listdir(current_dir):
    if filename.endswith('.py') and filename not in EXCLUDED_FILES:
        module_name = filename[:-3]  # strip .py
        module = importlib.import_module(module_name)
        if hasattr(module, 'bp'):
            app.register_blueprint(module.bp)
        else:
            print(f"Warning: {module_name}.py has no 'bp' Blueprint.")

if __name__ == '__main__':
    app.run(port=5000)
