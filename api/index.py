import os
import sys

# Add backend/ to sys.path so `from app import create_app` resolves
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app import create_app  # noqa: E402

app = create_app()
