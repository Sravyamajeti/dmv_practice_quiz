import sys
import os

# Add the project root to the path so we can import from backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.main import handler
