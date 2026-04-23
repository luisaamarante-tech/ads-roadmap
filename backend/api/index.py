import sys
import os

# Add backend/ to sys.path so `from app import create_app` resolves correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app

app = create_app()
