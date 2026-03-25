import os
import sys

# Because we have an 'app' package and 'app.py' module, we need to load 'app.py' as a module manually
import importlib.util
spec = importlib.util.spec_from_file_location("monolithic_app", "app.py")
monolithic_app = importlib.util.module_from_spec(spec)
sys.modules["monolithic_app"] = monolithic_app
spec.loader.exec_module(monolithic_app)

app = monolithic_app.app
db = monolithic_app.db

with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
