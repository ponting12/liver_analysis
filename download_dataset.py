"""
download_dataset.py - Entrypoint router for Streamlit Cloud and local runs.
If executed by Streamlit (or as main script), it runs/redirects to app.py so the user sees the dashboard immediately!
"""
import os
import sys

# Check if running in a Streamlit context or if called as the main file
app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")

if os.path.exists(app_path):
    # Execute app.py in the current namespace so Streamlit runs the dashboard directly!
    with open(app_path, "r", encoding="utf-8") as f:
        code = f.read()
    exec(code, globals())
else:
    print("app.py not found.")
