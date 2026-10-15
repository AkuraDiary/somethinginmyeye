"""Training and evaluation utilities for Elkinematics."""
import sys
import os

# Automatically add parent scripts directory to sys.path so config and universal_pipeline are accessible
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
